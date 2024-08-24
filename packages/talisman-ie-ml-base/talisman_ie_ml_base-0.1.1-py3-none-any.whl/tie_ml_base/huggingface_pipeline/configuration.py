from typing import Type

from tp_interfaces.abstract import AbstractDocumentProcessor, ModelTypeFactory


def _get_pipeline() -> Type[AbstractDocumentProcessor]:
    from tie_ml_base.huggingface_pipeline.wrapper import HuggingFacePipelineWrapper
    return HuggingFacePipelineWrapper


HF_PROCESSORS = ModelTypeFactory({
    "huggingface_pipeline": _get_pipeline,
})
