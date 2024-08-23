import pytest
import torch
import torch.nn as nn
from skim.model_comparison.compare import set_seed, compare_models

class SimpleModel(nn.Module):
    def __init__(self):
        super().__init__()
        self.conv = nn.Conv2d(1, 1, 3, padding=1)

    def forward(self, x):
        return self.conv(x)

class AnotherModel(nn.Module):
    def __init__(self):
        super().__init__()
        self.conv = nn.Conv2d(1, 1, 3, padding=1)
        self.relu = nn.ReLU()

    def forward(self, x):
        return self.relu(self.conv(x))

class NaiveModel(nn.Module):
    def __init__(self):
        super().__init__()
        self.conv1 = nn.Conv2d(1, 1, 3, padding=1)
        self.relu1 = nn.ReLU()
        self.conv2 = nn.Conv2d(1, 1, 3, padding=1)
        self.relu2 = nn.ReLU()
        self.conv3 = nn.Conv2d(1, 1, 3, padding=1)
        self.relu3 = nn.ReLU()

    def forward(self, x):
        x = self.conv1(x)
        x = self.relu1(x)
        x = self.conv2(x)
        x = self.relu2(x)
        x = self.conv3(x)
        x = self.relu3(x)
        return x

class SimpleBlock(nn.Module):
    def __init__(self):
        super().__init__()
        self.conv = nn.Conv2d(1, 1, 3, padding=1)
        self.relu = nn.ReLU()

    def forward(self, x):
        x = self.conv(x)
        x = self.relu(x)
        return x

class ModelWithBlocks(nn.Module):
    def __init__(self):
        super().__init__()
        self.blocks = nn.ModuleList([SimpleBlock() for _ in range(3)])

    def forward(self, x):
        for block in self.blocks:
            x = block(x)
        return x

def test_set_seed():
    set_seed(42)
    tensor1 = torch.randn(10, 10)
    
    set_seed(42)
    tensor2 = torch.randn(10, 10)
    
    assert torch.all(tensor1.eq(tensor2))

def test_compare_identical():
    naive_model = NaiveModel
    blocks_model = [ModelWithBlocks]

    input_shape = (1, 1, 30, 30)
    
    result = compare_models(naive_model, blocks_model, input_shape)
    dev_model = result["comparison_models"][0]

    max_diff_small = dev_model["max_diff"] < 1e-5
    mean_diff_small = dev_model["mean_diff"] < 1e-6
    std_diff_small = dev_model["std_diff"] < 1e-6

    assert max_diff_small, "Maximum difference should be very small"
    assert mean_diff_small, "Mean difference should be very small"
    assert std_diff_small, "Standard deviation of differences should be very small"


def test_compare_models():
    base_model = SimpleModel
    other_models = [AnotherModel]
    input_shape = (1, 1, 10, 10)
    
    result = compare_models(base_model, other_models, input_shape)
    
    assert "base_model" in result
    assert "comparison_models" in result
    assert isinstance(result["comparison_models"], list)
    assert len(result["comparison_models"]) == 1

    base_result = result["base_model"]
    assert "name" in base_result
    assert "output_shape" in base_result
    assert "output_sum" in base_result
    assert "param_count" in base_result

    comparison_result = result["comparison_models"][0]
    assert "name" in comparison_result
    assert "output_shape" in comparison_result
    assert "output_sum" in comparison_result
    assert "param_count" in comparison_result
    assert "max_diff" in comparison_result
    assert "mean_diff" in comparison_result
    assert "std_diff" in comparison_result

def test_compare_models_output():
    base_model = SimpleModel
    other_models = [AnotherModel]
    input_shape = (1, 1, 10, 10)
    
    result = compare_models(base_model, other_models, input_shape)
    
    base_result = result["base_model"]
    comparison_result = result["comparison_models"][0]
    
    assert base_result["name"] == "SimpleModel"
    assert base_result["output_shape"] == torch.Size([1, 1, 10, 10])
    assert isinstance(base_result["output_sum"], float)
    assert base_result["param_count"] > 0
    
    assert comparison_result["name"] == "AnotherModel"
    assert comparison_result["output_shape"] == torch.Size([1, 1, 10, 10])
    assert isinstance(comparison_result["output_sum"], float)
    assert comparison_result["param_count"] > 0
    assert isinstance(comparison_result["max_diff"], float)
    assert isinstance(comparison_result["mean_diff"], float)
    assert isinstance(comparison_result["std_diff"], float)

def test_compare_models_deterministic():
    base_model = SimpleModel
    other_models = [AnotherModel]
    input_shape = (1, 1, 10, 10)
    
    result1 = compare_models(base_model, other_models, input_shape, seed=42)
    result2 = compare_models(base_model, other_models, input_shape, seed=42)
    
    assert result1["base_model"]["output_sum"] == result2["base_model"]["output_sum"]
    assert result1["comparison_models"][0]["output_sum"] == result2["comparison_models"][0]["output_sum"]

if __name__ == "__main__":
    pytest.main()