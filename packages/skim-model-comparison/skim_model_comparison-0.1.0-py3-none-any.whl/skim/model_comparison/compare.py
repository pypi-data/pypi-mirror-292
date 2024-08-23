from typing import Type, List, Tuple, TypedDict
import torch
import torch.nn as nn

class ModelResult(TypedDict):
    name: str
    output_shape: torch.Size
    output_sum: float
    param_count: int

class ComparisonModelResult(ModelResult):
    max_diff: float
    mean_diff: float
    std_diff: float

class CompareModelsResult(TypedDict):
    base_model: ModelResult
    comparison_models: List[ComparisonModelResult]

def set_seed(seed: int) -> None:
    torch.manual_seed(seed)
    torch.cuda.manual_seed(seed)
    torch.cuda.manual_seed_all(seed)
    torch.backends.cudnn.deterministic = True
    torch.backends.cudnn.benchmark = False

def compare_models(base_model: Type[nn.Module], other_models: List[Type[nn.Module]], 
                   input_shape: Tuple[int, int, int, int] = (1, 1, 224, 224), 
                   seed: int = 42) -> CompareModelsResult:
    results: CompareModelsResult = {
        "base_model": ModelResult(),
        "comparison_models": []
    }

    # Run base model
    set_seed(seed)
    base = base_model()
    x = torch.randn(input_shape)
    base_output = base.forward(x)

    results["base_model"] = ModelResult(
        name=base_model.__name__,
        output_shape=base_output.shape,
        output_sum=base_output.sum().item(),
        param_count=sum(p.numel() for p in base.parameters())
    )

    # Run and compare other models
    for model_class in other_models:
        set_seed(seed)  # Reset seed for each model
        model = model_class()
        x = torch.randn(input_shape)  # Regenerate input with same seed
        output = model(x)
        diff = torch.abs(output - base_output)
        
        comparison_result = ComparisonModelResult(
            name=model_class.__name__,
            output_shape=output.shape,
            output_sum=output.sum().item(),
            param_count=sum(p.numel() for p in model.parameters()),
            max_diff=diff.max().item(),
            mean_diff=diff.mean().item(),
            std_diff=diff.std().item()
        )
        results["comparison_models"].append(comparison_result)

    return results