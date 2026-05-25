# 智能法律咨询机器人

基于 DeepSeek API 的多场景智能法律咨询系统，提供普通用户和专业律师两种咨询模式，支持实时风险评估、法律文书生成、多轮对话历史管理等功能。

## 项目简介
本项目是一个功能完善的智能法律咨询 Web 应用，通过调用 DeepSeek 大语言模型 API，为用户提供专业的法律咨询服务。系统能够自动识别民事、刑事、劳动三大法律领域，并根据用户输入进行风险评估，同时支持法律文书的智能生成与导出。

## 核心功能

1. 双模式咨询
普通模式：面向普通用户，提供通俗易懂的法律建议，回答简洁实用

专业模式：面向律师/法律从业者，使用法言法语，提供深度的法律技术分析

2. 智能场景识别
自动识别用户问题所属领域：

 民事纠纷（借贷、离婚、房产、合同等）

 刑事法律（盗窃、诈骗、故意伤害等）

 劳动仲裁（工资、辞退、工伤、社保等）

3. 风险评估系统
高风险：涉及人身安全、重大财产风险、刑事强制措施 → 红色预警

中风险：涉及诉讼、仲裁、维权紧迫事项 → 黄色提醒

低风险：一般法律咨询 → 蓝色提示

4. 法律文书智能生成
支持生成以下文书（专业模式）：

民事起诉状

民事答辩状

劳动仲裁申请书

合同条款建议

支持导出为 TXT 或 Word 格式

5. 会话历史管理
本地存储对话历史（普通/专业模式隔离）

历史对话随时回溯查看

支持新建对话、清空历史

6. 典型案例库 & 普法视频
内置民事、劳动、刑事典型案例（点击即可咨询）

嵌入式 B站普法视频（无需跳转）

7. 压力测试工具
附带独立压力测试脚本，可测试系统在高并发下的性能表现，生成可视化报告。

## 技术栈

组件	技术
后端框架	Flask
数据库	SQLite + SQLAlchemy
AI 模型	DeepSeek API
前端	HTML5/CSS3/JavaScript + Axios
文档导出	python-docx
压力测试	Python + Matplotlib
项目结构
text
├── app.py              # Flask 主程序
├── stress.py           # 压力测试工具
├── start.bat           # Windows 启动脚本
├── templates/
│   └── index.html      # 前端页面
└── chat.db             # SQLite 数据库（自动生成）

快速开始
环境要求
Python 3.8+

pip

安装依赖
bash
pip install flask flask-sqlalchemy requests python-docx matplotlib
配置 API Key
打开 app.py，修改 DeepSeek API Key：

python
DEEPSEEK_API_KEY = "your-api-key-here"
启动服务
方式一：直接运行

bash
python app.py
方式二：Windows 批处理

bash
start.bat
访问地址
本地访问：http://localhost:5003

同网络设备：http://[你的IP]:5003

压力测试
运行独立压力测试工具：

bash
python stress.py
功能特性：

支持普通模式/专业模式测试

支持自定义并发数和总请求数

自动生成性能报告（成功率、响应时间分布、百分位数等）

生成可视化图表（响应时间分布、趋势、成功率饼图、百分位数条形图）

测试示例
text
选择测试模式:
1. 快速测试 (10并发, 50请求)
2. 轻度压力 (5并发, 30请求)
3. 中度压力 (15并发, 100请求)
4. 重度压力 (30并发, 200请求)
5. 自定义测试
API 接口
端点	方法	说明
/chat	POST	普通模式聊天
/chat-pro	POST	专业模式聊天
/generate-document	POST	生成法律文书
/export-document	POST	导出文书文件
/pro-stat	GET	获取专业模式统计数据
/risk-logs	GET	获取风险日志
/stress-test	POST	压力测试
/test-result	GET	获取测试结果

界面预览
桌面端三栏布局
左侧：对话历史记录

中央：聊天主区域 + 专业工具箱 + 文书生成面板

右侧：典型案例库 + 普法视频
<img width="2000" height="938" alt="image" src="https://github.com/user-attachments/assets/c0efe302-f541-4f01-97ce-424c7a38d0c6" />


移动端适配
底部导航栏（历史/案例/视频）

侧滑抽屉菜单

浮动操作按钮

响应式布局，触摸友好
<img width="506" height="925" alt="image" src="https://github.com/user-attachments/assets/319e73f2-ee57-40f6-80e9-72b7bb526227" />

注意事项
法律免责声明：本系统回答仅供参考，不构成正式法律意见，复杂案件建议咨询执业律师

API 费用：使用 DeepSeek API 会产生费用，请确保账户余额充足

数据存储：对话历史存储在浏览器本地，清空缓存会丢失

网络要求：需要能够访问 DeepSeek API（国内正常访问）

后续优化建议
接入更多法律知识库（RAG 增强）

支持多用户登录与云端历史同步

增加法律条款原文检索功能

支持语音输入

接入微信公众号/小程序
