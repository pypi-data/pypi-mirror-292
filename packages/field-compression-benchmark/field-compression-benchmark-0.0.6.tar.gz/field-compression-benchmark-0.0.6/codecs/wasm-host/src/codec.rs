use std::{borrow::BorrowMut, sync::Arc};

use ndarray::{ArrayBase, ArrayView, Data, Dimension};
use numcodecs::{AnyArray, AnyArrayView, AnyArrayViewMut, AnyCowArray};
use serde::Serializer;
use wasm_component_layer::{
    List, ListType, Record, RecordType, ResourceOwn, Value, ValueType, Variant, VariantCase,
    VariantType,
};

use core_error::LocationError;

use crate::{
    error::{GuestError, RuntimeError},
    plugin::CodecPlugin,
    wit::guest_error_from_wasm,
};

#[allow(clippy::module_name_repetitions)]
pub struct WasmCodec<P: BorrowMut<CodecPlugin> = CodecPlugin> {
    pub(crate) resource: ResourceOwn,
    pub(crate) plugin: P,
    pub(crate) instruction_counter: u64,
}

impl<P: BorrowMut<CodecPlugin>> WasmCodec<P> {
    #[must_use]
    pub const fn instruction_counter(&self) -> u64 {
        self.instruction_counter
    }

    #[allow(clippy::type_complexity)]
    #[allow(clippy::needless_pass_by_value)]
    pub fn encode(
        &mut self,
        data: AnyCowArray,
    ) -> Result<Result<AnyArray, GuestError>, LocationError<RuntimeError>> {
        self.process(
            data.view(),
            |plugin, arguments, results| plugin.ctx.call_func(&plugin.encode, arguments, results),
            |encoded| Ok(encoded.into_owned()),
        )
    }

    #[allow(clippy::type_complexity)]
    #[allow(clippy::needless_pass_by_value)]
    pub fn encode_into(
        &mut self,
        data: AnyCowArray,
        mut encoded: AnyArrayViewMut,
    ) -> Result<Result<(), GuestError>, LocationError<RuntimeError>> {
        self.process(
            data.view(),
            |plugin, arguments, results| plugin.ctx.call_func(&plugin.encode, arguments, results),
            |encoded_in| {
                encoded
                    .assign(&encoded_in)
                    .map_err(anyhow::Error::new)
                    .map_err(LocationError::from2)
            },
        )
    }

    #[allow(clippy::type_complexity)]
    #[allow(clippy::needless_pass_by_value)]
    pub fn decode(
        &mut self,
        encoded: AnyCowArray,
    ) -> Result<Result<AnyArray, GuestError>, LocationError<RuntimeError>> {
        self.process(
            encoded.view(),
            |plugin, arguments, results| plugin.ctx.call_func(&plugin.decode, arguments, results),
            |decoded| Ok(decoded.into_owned()),
        )
    }

    #[allow(clippy::type_complexity)]
    #[allow(clippy::needless_pass_by_value)]
    pub fn decode_into(
        &mut self,
        encoded: AnyArrayView,
        mut decoded: AnyArrayViewMut,
    ) -> Result<Result<(), GuestError>, LocationError<RuntimeError>> {
        self.process(
            encoded,
            |plugin, arguments, results| plugin.ctx.call_func(&plugin.decode, arguments, results),
            |decoded_in| {
                decoded
                    .assign(&decoded_in)
                    .map_err(anyhow::Error::new)
                    .map_err(LocationError::from2)
            },
        )
    }

    pub fn get_config<S: Serializer>(&mut self, serializer: S) -> Result<S::Ok, S::Error> {
        let plugin: &mut CodecPlugin = self.plugin.borrow_mut();

        let resource = plugin
            .ctx
            .borrow_resource(&self.resource)
            .map_err(serde::ser::Error::custom)?;

        let arg = Value::Borrow(resource);
        let mut result = Value::U8(0);

        plugin
            .ctx
            .call_func(
                &plugin.get_config,
                std::slice::from_ref(&arg),
                std::slice::from_mut(&mut result),
            )
            .map_err(serde::ser::Error::custom)?;

        let config = match result {
            Value::Result(result) => match &*result {
                Ok(Some(Value::String(config))) => config.clone(),
                Err(err) => match guest_error_from_wasm(err) {
                    Ok(err) => return Err(serde::ser::Error::custom(err)),
                    Err(err) => return Err(serde::ser::Error::custom(err)),
                },
                result => {
                    return Err(serde::ser::Error::custom(format!(
                        "unexpected get-config result value {result:?}"
                    )))
                },
            },
            value => {
                return Err(serde::ser::Error::custom(format!(
                    "unexpected get-config result value {value:?}"
                )))
            },
        };

        serde_transcode::transcode(&mut serde_json::Deserializer::from_str(&config), serializer)
    }

    pub fn drop(mut self) -> Result<(), LocationError<RuntimeError>> {
        let plugin: &mut CodecPlugin = self.plugin.borrow_mut();

        let result = plugin
            .ctx
            .drop_resource(&self.resource)
            .map_err(LocationError::from2);

        // We need to forget here instead of using ManuallyDrop since we need
        //  both a mutable borrow to self.plugin and an immutable borrow to
        //  self.resource at the same time
        std::mem::forget(self);

        result
    }
}

impl<P: BorrowMut<CodecPlugin>> WasmCodec<P> {
    #[allow(clippy::type_complexity)]
    fn process<O>(
        &mut self,
        data: AnyArrayView,
        process: impl FnOnce(&mut CodecPlugin, &[Value], &mut [Value]) -> anyhow::Result<()>,
        with_result: impl for<'a> FnOnce(AnyArrayView<'a>) -> Result<O, LocationError<RuntimeError>>,
    ) -> Result<Result<O, GuestError>, LocationError<RuntimeError>> {
        let plugin: &mut CodecPlugin = self.plugin.borrow_mut();

        let resource = plugin
            .ctx
            .borrow_resource(&self.resource)
            .map_err(LocationError::from2)?;

        let any_array_data_ty = Self::any_array_data_ty()?;
        let any_array_ty = Self::any_array_ty(any_array_data_ty.clone())?;

        let array = Self::array_into_wasm(data, any_array_ty, any_array_data_ty.clone())?;

        let instruction_counter_pre = plugin
            .ctx
            .call_typed_u64_func(&plugin.instruction_counter)
            .map_err(LocationError::from2)?;

        let mut result = Value::U8(0);

        process(
            plugin,
            &[Value::Borrow(resource), Value::Record(array)],
            std::slice::from_mut(&mut result),
        )
        .map_err(LocationError::from2)?;

        let instruction_counter_post = plugin
            .ctx
            .call_typed_u64_func(&plugin.instruction_counter)
            .map_err(LocationError::from2)?;
        self.instruction_counter += instruction_counter_post - instruction_counter_pre;

        match result {
            Value::Result(result) => match &*result {
                Ok(Some(Value::Record(record)))
                    if record.ty() == Self::any_array_ty(any_array_data_ty)? =>
                {
                    Self::with_array_view_from_wasm_record(record, |array| {
                        Ok(Ok(with_result(array)?))
                    })
                },
                Err(err) => guest_error_from_wasm(err).map(Err),
                result => Err(LocationError::from2(anyhow::Error::msg(format!(
                    "unexpected process result value {result:?}"
                )))),
            },
            value => Err(LocationError::from2(anyhow::Error::msg(format!(
                "unexpected process result value {value:?}"
            )))),
        }
    }

    fn any_array_data_ty() -> Result<VariantType, LocationError<RuntimeError>> {
        let any_array_data_ty = VariantType::new(
            None,
            [
                VariantCase::new("u8", Some(ValueType::List(ListType::new(ValueType::U8)))),
                VariantCase::new("u16", Some(ValueType::List(ListType::new(ValueType::U16)))),
                VariantCase::new("u32", Some(ValueType::List(ListType::new(ValueType::U32)))),
                VariantCase::new("u64", Some(ValueType::List(ListType::new(ValueType::U64)))),
                VariantCase::new("i8", Some(ValueType::List(ListType::new(ValueType::S8)))),
                VariantCase::new("i16", Some(ValueType::List(ListType::new(ValueType::S16)))),
                VariantCase::new("i32", Some(ValueType::List(ListType::new(ValueType::S32)))),
                VariantCase::new("i64", Some(ValueType::List(ListType::new(ValueType::S64)))),
                VariantCase::new("f32", Some(ValueType::List(ListType::new(ValueType::F32)))),
                VariantCase::new("f64", Some(ValueType::List(ListType::new(ValueType::F64)))),
            ],
        )
        .map_err(LocationError::from2)?;

        Ok(any_array_data_ty)
    }

    fn any_array_ty(
        any_array_data_ty: VariantType,
    ) -> Result<RecordType, LocationError<RuntimeError>> {
        let any_array_ty = RecordType::new(
            None,
            [
                ("data", ValueType::Variant(any_array_data_ty)),
                ("shape", ValueType::List(ListType::new(ValueType::U32))),
            ],
        )
        .map_err(LocationError::from2)?;

        Ok(any_array_ty)
    }

    #[allow(clippy::needless_pass_by_value)]
    fn array_into_wasm(
        array: AnyArrayView,
        any_array_ty: RecordType,
        any_array_data_ty: VariantType,
    ) -> Result<Record, LocationError<RuntimeError>> {
        fn list_from_standard_layout<'a, T: 'static + Copy, S: Data<Elem = T>, D: Dimension>(
            array: &'a ArrayBase<S, D>,
        ) -> List
        where
            List: From<&'a [T]> + From<Arc<[T]>>,
        {
            #[allow(clippy::option_if_let_else)]
            if let Some(slice) = array.as_slice() {
                List::from(slice)
            } else {
                List::from(Arc::from(array.iter().copied().collect::<Vec<T>>()))
            }
        }

        let data = match &array {
            AnyArrayView::U8(array) => Variant::new(
                any_array_data_ty,
                0,
                Some(Value::List(list_from_standard_layout(array))),
            ),
            AnyArrayView::U16(array) => Variant::new(
                any_array_data_ty,
                1,
                Some(Value::List(list_from_standard_layout(array))),
            ),
            AnyArrayView::U32(array) => Variant::new(
                any_array_data_ty,
                2,
                Some(Value::List(list_from_standard_layout(array))),
            ),
            AnyArrayView::U64(array) => Variant::new(
                any_array_data_ty,
                3,
                Some(Value::List(list_from_standard_layout(array))),
            ),
            AnyArrayView::I8(array) => Variant::new(
                any_array_data_ty,
                4,
                Some(Value::List(list_from_standard_layout(array))),
            ),
            AnyArrayView::I16(array) => Variant::new(
                any_array_data_ty,
                5,
                Some(Value::List(list_from_standard_layout(array))),
            ),
            AnyArrayView::I32(array) => Variant::new(
                any_array_data_ty,
                6,
                Some(Value::List(list_from_standard_layout(array))),
            ),
            AnyArrayView::I64(array) => Variant::new(
                any_array_data_ty,
                7,
                Some(Value::List(list_from_standard_layout(array))),
            ),
            AnyArrayView::F32(array) => Variant::new(
                any_array_data_ty,
                8,
                Some(Value::List(list_from_standard_layout(array))),
            ),
            AnyArrayView::F64(array) => Variant::new(
                any_array_data_ty,
                9,
                Some(Value::List(list_from_standard_layout(array))),
            ),
            array => Err(anyhow::Error::msg(format!(
                "unknown array dtype type {}",
                array.dtype()
            ))),
        }
        .map_err(LocationError::from2)?;

        let shape = array
            .shape()
            .iter()
            .map(|s| u32::try_from(*s))
            .collect::<Result<Vec<_>, _>>()
            .map_err(anyhow::Error::new)
            .map_err(LocationError::from2)?;
        let shape = List::from(Arc::from(shape));

        Record::new(
            any_array_ty,
            [
                ("data", Value::Variant(data)),
                ("shape", Value::List(shape)),
            ],
        )
        .map_err(LocationError::from2)
    }

    #[allow(clippy::too_many_lines)] // FIXME
    fn with_array_view_from_wasm_record<O>(
        record: &Record,
        with: impl for<'a> FnOnce(AnyArrayView<'a>) -> Result<O, LocationError<RuntimeError>>,
    ) -> Result<O, LocationError<RuntimeError>> {
        let Some(Value::List(shape)) = record.field("shape") else {
            return Err(LocationError::from2(anyhow::Error::msg(format!(
                "process result record {record:?} is missing shape field"
            ))));
        };
        let shape = shape
            .typed::<u32>()
            .map_err(LocationError::from2)?
            .iter()
            .copied()
            .map(usize::try_from)
            .collect::<Result<Vec<_>, _>>()
            .map_err(anyhow::Error::new)
            .map_err(LocationError::from2)?;

        let Some(Value::Variant(data)) = record.field("data") else {
            return Err(LocationError::from2(anyhow::Error::msg(format!(
                "process result record {record:?} is missing data field"
            ))));
        };
        let Some(Value::List(values)) = data.value() else {
            return Err(LocationError::from2(anyhow::Error::msg(format!(
                "process result buffer has an invalid variant type {:?}",
                data.value().map(|v| v.ty())
            ))));
        };

        let array = match data.discriminant() {
            0 => AnyArrayView::U8(
                ArrayView::from_shape(
                    shape.as_slice(),
                    values.typed().map_err(LocationError::from2)?,
                )
                .map_err(anyhow::Error::new)
                .map_err(LocationError::from2)?,
            ),
            1 => AnyArrayView::U16(
                ArrayView::from_shape(
                    shape.as_slice(),
                    values.typed().map_err(LocationError::from2)?,
                )
                .map_err(anyhow::Error::new)
                .map_err(LocationError::from2)?,
            ),
            2 => AnyArrayView::U32(
                ArrayView::from_shape(
                    shape.as_slice(),
                    values.typed().map_err(LocationError::from2)?,
                )
                .map_err(anyhow::Error::new)
                .map_err(LocationError::from2)?,
            ),
            3 => AnyArrayView::U64(
                ArrayView::from_shape(
                    shape.as_slice(),
                    values.typed().map_err(LocationError::from2)?,
                )
                .map_err(anyhow::Error::new)
                .map_err(LocationError::from2)?,
            ),
            4 => AnyArrayView::I8(
                ArrayView::from_shape(
                    shape.as_slice(),
                    values.typed().map_err(LocationError::from2)?,
                )
                .map_err(anyhow::Error::new)
                .map_err(LocationError::from2)?,
            ),
            5 => AnyArrayView::I16(
                ArrayView::from_shape(
                    shape.as_slice(),
                    values.typed().map_err(LocationError::from2)?,
                )
                .map_err(anyhow::Error::new)
                .map_err(LocationError::from2)?,
            ),
            6 => AnyArrayView::I32(
                ArrayView::from_shape(
                    shape.as_slice(),
                    values.typed().map_err(LocationError::from2)?,
                )
                .map_err(anyhow::Error::new)
                .map_err(LocationError::from2)?,
            ),
            7 => AnyArrayView::I64(
                ArrayView::from_shape(
                    shape.as_slice(),
                    values.typed().map_err(LocationError::from2)?,
                )
                .map_err(anyhow::Error::new)
                .map_err(LocationError::from2)?,
            ),
            8 => AnyArrayView::F32(
                ArrayView::from_shape(
                    shape.as_slice(),
                    values.typed().map_err(LocationError::from2)?,
                )
                .map_err(anyhow::Error::new)
                .map_err(LocationError::from2)?,
            ),
            9 => AnyArrayView::F64(
                ArrayView::from_shape(
                    shape.as_slice(),
                    values.typed().map_err(LocationError::from2)?,
                )
                .map_err(anyhow::Error::new)
                .map_err(LocationError::from2)?,
            ),
            discriminant => {
                return Err(LocationError::from2(anyhow::Error::msg(format!(
                    "process result buffer has an invalid variant [{discriminant}]:{:?}",
                    data.value().map(|v| v.ty())
                ))))
            },
        };

        with(array)
    }
}

impl<P: BorrowMut<CodecPlugin>> Drop for WasmCodec<P> {
    fn drop(&mut self) {
        let plugin: &mut CodecPlugin = self.plugin.borrow_mut();

        std::mem::drop(plugin.ctx.drop_resource(&self.resource));
    }
}
