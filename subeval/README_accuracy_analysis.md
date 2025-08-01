# 准确率分析脚本使用说明

## 概述

`accuracy_analysis.py` 是一个用于分析主观评测结果的Python脚本，专门用于分析中文强调意图识别任务中两个模型（Gemini和StressTransfer）的表现。

## 功能特性

1. **准确率计算**: 计算每个模型的准确率
2. **配对分析**: 分析相同样本上两个模型的表现对比
3. **示例展示**: 提供中文强调意图分析的参考示例
4. **详细报告**: 生成完整的分析报告

## 使用方法

### 基本用法

```bash
# 分析评测结果文件
python3 accuracy_analysis.py <评测结果文件路径>
```

示例：
```bash
python3 accuracy_analysis.py evaluation_results_2025-07-29T08-21-47-143Z.txt
```

### 查看分析示例

```bash
# 仅查看中文强调意图分析示例
python3 accuracy_analysis.py --examples
```

### 同时查看示例和分析结果

```bash
# 先显示示例，再分析评测结果
python3 accuracy_analysis.py evaluation_results_2025-07-29T08-21-47-143Z.txt --examples
```

## 中文强调意图分析示例

脚本包含4个典型的中文强调意图分析示例：

### 示例1: 强调动作
- **句子**: 我没有说他*偷*了钱。
- **分析**: 强调"偷"这个动作，暗示他可能通过其他方式获得钱财
- **正确答案**: 选项1（可能是借的或者捡到的，但他没有偷）

### 示例2: 强调主体
- **句子**: 不是*我*拿走了你的书。
- **分析**: 强调"我"，暗示是别人而不是说话者本人
- **正确答案**: 选项2（也可能是别人拿的，但不是我）

### 示例3: 强调动作方式
- **句子**: 我没有*偷*这辆车。
- **分析**: 强调"偷"这个动作，暗示通过合法方式获得车辆
- **正确答案**: 选项1（我借了这辆车）

### 示例4: 强调表达方式
- **句子**: 她*说*她很抱歉。
- **分析**: 强调"说"这个动作，暗示只是口头表达，可能不是真心的
- **正确答案**: 选项2（她并不是真心的）

## 输出报告说明

### 基本信息
- **总样本数**: 评测数据集中的总样本数量
- **已评测数**: 已完成评测的样本数量
- **完成配对评测的样本数**: 两个模型都完成评测的样本数量

### 准确率统计
- 显示每个模型的正确答案数和准确率百分比
- 正确答案定义：选择选项1或选项2（"以上都不是"被认为是错误答案）

### 配对比较分析
- **两模型结果相同**: 两个模型给出相同答案的样本比例
- **两模型都正确**: 两个模型都给出正确答案的样本比例
- **两模型都错误**: 两个模型都给出错误答案的样本比例
- **仅某模型正确**: 只有一个模型给出正确答案的样本比例

### 相对性能
- 比较两个模型的相对表现，判断哪个模型表现更好或是否相当

## 评测标准

在中文强调意图分析任务中：
- **正确答案**: 选项1或选项2（具体的意图解释）
- **错误答案**: 选项3（"以上都不是"）

这个标准基于强调词通常都有特定的语用意图，很少出现"以上都不是"的情况。

## 注意事项

1. 确保评测结果文件格式正确，包含必要的统计信息和详细结果
2. 脚本假设模型名称为"Gemini"和"StressTransfer"
3. 文件编码应为UTF-8以正确处理中文内容
4. 如果遇到解析错误，请检查评测结果文件的格式是否符合预期

## 依赖要求

- Python 3.x
- 标准库：re, sys, collections

无需安装额外的第三方包。