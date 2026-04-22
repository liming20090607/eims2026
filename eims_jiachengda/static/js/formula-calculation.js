/**
 * 数值输入框公式计算功能
 * 支持在数值输入框中输入简单公式，自动计算结果
 * 
 * 支持的公式格式：
 * - 3+2 (直接输入算式)
 * - =3+2 (带等号)
 * - 10*5 (乘法)
 * - 100/4 (除法)
 * - 10-3+2 (混合运算)
 * - (3+2)*10 (带括号)
 * 
 * 使用方法：
 * 1. 在输入框中输入公式
 * 2. 按下 Enter 键或失去焦点时自动计算
 * 3. 计算结果自动填入输入框
 */

(function() {
    'use strict';

    // 安全的数学表达式计算函数
    function safeCalculate(expression) {
        try {
            // 1. 移除所有非数学字符（只保留数字、运算符、括号、小数点、空格、百分号）
            let cleanExpr = expression.replace(/[^0-9+\-*/().%\s]/g, '');
            
            // 2. 检查是否为空
            if (!cleanExpr || cleanExpr.trim() === '') {
                return null;
            }
            
            // 3. 处理百分号：将 % 替换为 /100
            cleanExpr = cleanExpr.replace(/(\d+(\.\d+)?)%/g, '$1/100');
            
            // 4. 检查是否只包含数字（没有运算符）
            if (/^\s*-?\d+(\.\d+)?\s*$/.test(cleanExpr)) {
                return parseFloat(cleanExpr);
            }
            
            // 5. 验证表达式安全性（只允许数学运算）
            const validPattern = /^[\d+\-*/().\s]+$/;
            if (!validPattern.test(cleanExpr)) {
                console.warn('Invalid expression:', cleanExpr);
                return null;
            }
            
            // 6. 使用 Function 构造函数安全计算（比 eval 更安全）
            // 只返回计算结果，不执行其他代码
            const result = new Function('return ' + cleanExpr)();
            
            // 7. 验证结果是否为有效数字
            if (typeof result === 'number' && !isNaN(result) && isFinite(result)) {
                return result;
            }
            
            return null;
        } catch (error) {
            console.warn('Calculation error:', error);
            return null;
        }
    }

    // 格式化结果为 2 位小数
    function formatResult(value) {
        if (value === null || value === undefined) {
            return '';
        }
        // 四舍五入到 2 位小数
        return Number(value.toFixed(2)).toString();
    }

    // 处理输入框的公式计算
    function handleFormulaCalculation(input) {
        const originalValue = input.value.trim();
        
        // 如果没有值，跳过
        if (!originalValue) {
            return;
        }
        
        // 检查是否包含公式特征（等号或运算符）
        const isFormula = originalValue.startsWith('=') || 
                         /[+\-*/]/.test(originalValue.replace(/[-+*/.]/g, '')) && 
                         /[+\-*/]/.test(originalValue);
        
        if (!isFormula) {
            return;
        }
        
        // 移除等号（如果有）
        let expression = originalValue.replace(/^=/, '');
        
        // 计算表达式
        const result = safeCalculate(expression);
        
        if (result !== null) {
            // 格式化结果
            const formattedResult = formatResult(result);
            
            // 填入输入框
            input.value = formattedResult;
            
            // 触发自定义事件（供其他代码使用）
            input.dispatchEvent(new CustomEvent('formula-calculated', {
                bubbles: true,
                detail: {
                    originalValue: originalValue,
                    calculatedValue: formattedResult,
                    result: result
                }
            }));
            
            console.log(`公式计算：${originalValue} = ${formattedResult}`);
        } else {
            console.warn(`公式计算失败：${originalValue}`);
        }
    }

    // 初始化所有数值输入框
    function initializeFormulaInputs() {
        // 查找所有数值输入框（包括 number 和 text 类型）
        const numberInputs = document.querySelectorAll('input[type="number"], input[type="text"][step], input[step]');
        
        numberInputs.forEach(function(input) {
            // 如果已经初始化过，跳过
            if (input.dataset.formulaInitialized === 'true') {
                return;
            }
            
            // 标记为已初始化
            input.dataset.formulaInitialized = 'true';
            
            // 监听失去焦点事件（blur）
            input.addEventListener('blur', function() {
                handleFormulaCalculation(this);
            });
            
            // 监听 Enter 键
            input.addEventListener('keydown', function(e) {
                if (e.key === 'Enter') {
                    e.preventDefault();
                    handleFormulaCalculation(this);
                    
                    // 自动跳到下一个输入框
                    const form = this.closest('form');
                    if (form) {
                        const inputs = Array.from(form.querySelectorAll('input[type="number"], input[type="text"][step], input[step]'));
                        const currentIndex = inputs.indexOf(this);
                        if (currentIndex < inputs.length - 1) {
                            inputs[currentIndex + 1].focus();
                            inputs[currentIndex + 1].select();
                        }
                    }
                }
            });
            
            // 监听输入事件 - 实时检测公式（可选，增强体验）
            let calculationTimer = null;
            input.addEventListener('input', function(e) {
                // 清除之前的定时器
                if (calculationTimer) {
                    clearTimeout(calculationTimer);
                }
                
                const value = this.value.trim();
                
                // 检测是否是公式
                const isFormula = value && (value.startsWith('=') || 
                    (value.includes('+') || value.includes('-') || 
                    value.includes('*') || value.includes('/') || 
                    value.includes('%')));
                
                if (isFormula) {
                    // 添加视觉提示（绿色边框）
                    this.style.borderColor = '#28a745';
                    this.style.backgroundColor = '#d4edda';
                    
                    // 延迟计算（用户停止输入后 500ms 计算）
                    calculationTimer = setTimeout(() => {
                        handleFormulaCalculation(this);
                        // 恢复样式
                        this.style.borderColor = '';
                        this.style.backgroundColor = '';
                    }, 500);
                } else {
                    // 恢复样式
                    this.style.borderColor = '';
                    this.style.backgroundColor = '';
                }
            });
            
            // 添加提示标题
            if (!input.title) {
                input.title = '支持公式计算，例如：3+2, =10*5, (3+2)*10, 100*30%';
            }
        });
    }

    // 页面加载完成后初始化
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', initializeFormulaInputs);
    } else {
        initializeFormulaInputs();
    }

    // 暴露全局函数（供外部调用）
    window.formulaCalculation = {
        calculate: safeCalculate,
        format: formatResult,
        handle: handleFormulaCalculation,
        init: initializeFormulaInputs
    };

})();
