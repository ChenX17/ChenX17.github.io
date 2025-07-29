#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
模型准确率分析脚本
分析主观评测结果，计算两个模型的准确率
"""

import re
import sys
from collections import defaultdict

def show_analysis_examples():
    """
    展示中文强调意图分析示例
    """
    print("="*80)
    print("中文强调意图分析示例")
    print("="*80)
    
    examples = [
        {
            "sentence": "我没有说他*偷*了钱。",
            "options": "1. 可能是借的或者捡到的，但他没有偷。 2. 是别人偷的，不是他。 3. 以上都不是",
            "analysis": "强调\"偷\"这个动作，暗示他可能通过其他方式获得钱财，但不是偷窃",
            "answer": "1"
        },
        {
            "sentence": "不是*我*拿走了你的书。",
            "options": "1. 可能是找到或借来的。 2. 也可能是别人拿的，但不是我。 3. 以上都不是",
            "analysis": "强调\"我\"，暗示是别人而不是说话者本人",
            "answer": "2"
        },
        {
            "sentence": "我没有*偷*这辆车。",
            "options": "1. 我借了这辆车。 2. 我偷了另一辆不同的车。 3. 以上都不是",
            "analysis": "强调\"偷\"这个动作，暗示通过合法方式（借用）获得车辆",
            "answer": "1"
        },
        {
            "sentence": "她*说*她很抱歉。",
            "options": "1. 是她道歉了，而不是别人。 2. 她并不是真心的。 3. 以上都不是",
            "analysis": "强调\"说\"这个动作，暗示只是口头表达，可能不是真心的",
            "answer": "2"
        }
    ]
    
    print("请分析以下中文句子中被*包围的强调词的可能的意图，并从给定选项中选择最符合的答案。\n")
    print("参考示例:\n")
    
    for i, example in enumerate(examples, 1):
        print(f"示例{i}:")
        print(f"句子：{example['sentence']}")
        print(f"选项：{example['options']}")
        print(f"分析：{example['analysis']}")
        print(f"答案：{example['answer']}\n")
    
    print("="*80)
    print()

def parse_evaluation_results(file_path):
    """
    解析评测结果文件
    """
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 提取基本统计信息
    total_samples = int(re.search(r'总样本数: (\d+)', content).group(1))
    evaluated_samples = int(re.search(r'已评测数: (\d+)', content).group(1))
    
    # 提取配对分析信息
    paired_samples = int(re.search(r'完成配对评测的样本数: (\d+)', content).group(1))
    same_results = int(re.search(r'两模型评测结果相同的样本数: (\d+)', content).group(1))
    
    # 解析详细评测结果
    sample_pattern = r'样本 \d+ \(原始ID: ([^,]+), 模型: ([^)]+)\):[\s\S]*?评测结果: ([^\n]+)'
    matches = re.findall(sample_pattern, content)
    
    results = []
    for original_id, model_name, result in matches:
        results.append({
            'original_id': original_id,
            'model_name': model_name,
            'result': result.strip()
        })
    
    return {
        'total_samples': total_samples,
        'evaluated_samples': evaluated_samples,
        'paired_samples': paired_samples,
        'same_results': same_results,
        'results': results
    }

def calculate_accuracy(data):
    """
    计算准确率
    这里假设选项1和选项2都是正确答案，"以上都不是"是错误答案
    """
    model_stats = defaultdict(lambda: {'correct': 0, 'total': 0})
    
    for result in data['results']:
        model_name = result['model_name']
        answer = result['result']
        
        model_stats[model_name]['total'] += 1
        
        # 如果选择了选项1或选项2，认为是正确的
        if answer in ['1', '2']:
            model_stats[model_name]['correct'] += 1
    
    # 计算准确率
    accuracy_results = {}
    for model_name, stats in model_stats.items():
        accuracy = stats['correct'] / stats['total'] if stats['total'] > 0 else 0
        accuracy_results[model_name] = {
            'correct': stats['correct'],
            'total': stats['total'],
            'accuracy': accuracy
        }
    
    return accuracy_results

def analyze_paired_results(data):
    """
    分析配对结果
    """
    paired_results = defaultdict(dict)
    
    # 按原始ID分组
    for result in data['results']:
        original_id = result['original_id']
        model_name = result['model_name']
        answer = result['result']
        
        paired_results[original_id][model_name] = answer
    
    # 分析配对比较
    comparison_stats = {
        'both_correct': 0,
        'both_wrong': 0,
        'gemini_better': 0,
        'stresstransfer_better': 0,
        'same_result': 0,
        'total_pairs': 0
    }
    
    for original_id, models in paired_results.items():
        if 'Gemini' in models and 'StressTransfer' in models:
            comparison_stats['total_pairs'] += 1
            
            gemini_answer = models['Gemini']
            st_answer = models['StressTransfer']
            
            gemini_correct = gemini_answer in ['1', '2']
            st_correct = st_answer in ['1', '2']
            
            if gemini_answer == st_answer:
                comparison_stats['same_result'] += 1
            
            if gemini_correct and st_correct:
                comparison_stats['both_correct'] += 1
            elif not gemini_correct and not st_correct:
                comparison_stats['both_wrong'] += 1
            elif gemini_correct and not st_correct:
                comparison_stats['gemini_better'] += 1
            elif not gemini_correct and st_correct:
                comparison_stats['stresstransfer_better'] += 1
    
    return comparison_stats

def print_analysis_report(data, accuracy_results, comparison_stats):
    """
    打印分析报告
    """
    print("=" * 60)
    print("模型准确率分析报告")
    print("=" * 60)
    
    print(f"\n基本信息:")
    print(f"总样本数: {data['total_samples']}")
    print(f"已评测数: {data['evaluated_samples']}")
    print(f"完成配对评测的样本数: {data['paired_samples']}")
    
    print(f"\n准确率统计:")
    for model_name, stats in accuracy_results.items():
        print(f"{model_name}:")
        print(f"  正确答案数: {stats['correct']}/{stats['total']}")
        print(f"  准确率: {stats['accuracy']:.2%}")
    
    print(f"\n配对比较分析:")
    print(f"总配对数: {comparison_stats['total_pairs']}")
    print(f"两模型结果相同: {comparison_stats['same_result']} ({comparison_stats['same_result']/comparison_stats['total_pairs']:.1%})")
    print(f"两模型都正确: {comparison_stats['both_correct']} ({comparison_stats['both_correct']/comparison_stats['total_pairs']:.1%})")
    print(f"两模型都错误: {comparison_stats['both_wrong']} ({comparison_stats['both_wrong']/comparison_stats['total_pairs']:.1%})")
    print(f"仅Gemini正确: {comparison_stats['gemini_better']} ({comparison_stats['gemini_better']/comparison_stats['total_pairs']:.1%})")
    print(f"仅StressTransfer正确: {comparison_stats['stresstransfer_better']} ({comparison_stats['stresstransfer_better']/comparison_stats['total_pairs']:.1%})")
    
    # 计算相对性能
    if comparison_stats['total_pairs'] > 0:
        gemini_advantage = comparison_stats['gemini_better'] - comparison_stats['stresstransfer_better']
        print(f"\n相对性能:")
        if gemini_advantage > 0:
            print(f"Gemini在{gemini_advantage}个样本上表现更好")
        elif gemini_advantage < 0:
            print(f"StressTransfer在{abs(gemini_advantage)}个样本上表现更好")
        else:
            print(f"两个模型表现相当")

def main():
    if len(sys.argv) < 2:
        print("使用方法: python accuracy_analysis.py <评测结果文件路径> [--examples]")
        print("选项:")
        print("  --examples: 显示中文强调意图分析示例")
        sys.exit(1)
    
    # 检查是否需要显示示例
    if '--examples' in sys.argv:
        show_analysis_examples()
        if len(sys.argv) == 2:  # 只有--examples参数
            return
    
    # 获取文件路径（排除--examples参数）
    file_path = None
    for arg in sys.argv[1:]:
        if not arg.startswith('--'):
            file_path = arg
            break
    
    if not file_path:
        print("错误: 请提供评测结果文件路径")
        sys.exit(1)
    
    try:
        # 解析评测结果
        data = parse_evaluation_results(file_path)
        
        # 计算准确率
        accuracy_results = calculate_accuracy(data)
        
        # 分析配对结果
        comparison_stats = analyze_paired_results(data)
        
        # 打印分析报告
        print_analysis_report(data, accuracy_results, comparison_stats)
        
    except Exception as e:
        print(f"分析过程中出现错误: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()