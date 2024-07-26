stop_words = set(['的', '了', '在', '是', '和', '与', '及', '或', '等', '也', '而', '但', '还', '只', '就','既','既然','立即','这家','公告','表示','主力',
    '以上','公司','人士','出炉','发生','相关','全年','万元','亿元','元','合作','机制','根据','历史','推迟','联合开发','部分','禁止','截止','中国','美国',
    '服务','产品','设备','其中','发生','准确','财联社','记者','通讯','消息','发布','电','报道','增加','地区','下降','分析','报告','走势','数据',
    '指数','上半年','亿美元','减少','预计','天期',' 下调','达到','下半年','全年',' 季度','上季度','财年','范围','通过','开始','市场','同比','环比',
    '今日','操作','长期','上午','下午','夜间','股份','有限','报价','涨跌','涨幅','跌幅','涨跌幅','涨跌额','幅度','百分比','年期','附近','进一步',
    '有望','应急','机构','继续','持续','显示','决定','重大','近期','全面','先进','时间','截止','问题','团队',
    '关于','方面','进行','当地','重点','日时','近日','规模','交易','做好','最高','研究','成为','信息','最大','宣布','比例','应用','新闻','快讯','新华社','通迅','来源','研究',
    '涨停','跌停','做好','公布','重大','应用','取消','预警','已经','影响','披露','中心','领域','以及','参与','驱动','运转','影响','机会','我们','正在','架次',' 小时',
    '会见',' 面临','交易','买卖','企业','如果',' 比安','系统','今年',' 本月','本周',' 过去','几周','上月','获得','披露','央行','回购','增长','此次','调整','合约',
    '美国','工厂','收入','跌超','每月','打开','下行','技术','国内','下调','居前','收益率','截至','制造','基点','高温','需求','涨超','协议','高开','回笼',
    '材料','到期','频繁','运行','运营','协议','居前','公开市场','上调','国家','区域','要求','以来','引发','加速','趋势','几个','省级','取得',
    '一定','市场份额','透露','提前','完成','提前完成','交付','目标','供应商','充分','受益','同步','功里','要素','形成','不当','联社','日电','提到','生产','畅通','流动','各类','高效','配置','释放',
    '用地','资本','基础','全国','一体化','知识','管理','评价','贡献','优化','阶梯',
    '定价','流通','体制','联网','一体','衔接','标准','降低',
    '调度','适当','原则上','本级','安排','支出','委托','代行','不得','配套','确需','行使','专项','转移','扩大','限制性',
    '措施','合理','积极','首发','完整','内需','有效',
    '落地','主导','内生','长久','各种',
    '行为','实行','注销','退出','聚焦','环节','取向','一致性',
    '分支机构','办法','逐步推广','主体','发生地','国际','大全','控股','股东','实控','及其','自愿','延期','解禁','所持','限售','股财','收到','开曼','实际','控制','之一',
    '先生','分别','出具','延长','锁定','期限','首次','公开','发行','前限售','数量','亿股','股本','年月日','如遇','节假日','自动','顺延',
    '对外','增财','业绩','快报','实现','营业','归属于','上市公司','净利润','同比增加','万股','集中','竞价','方式','用于','维护','价值','区间','上限',
    '超过','下限','不少','元股','不超','确定','严格','各级','负责人',
    '模式','超常','布局','急需',
    '简称','变更','名称',
    '清理','一般性','市县','同事','相匹配','程度','激励','约束','附加','合并','授权','具体','适用',
    '整合','内容','职能','作用','安全','风险','监测','应对','条件','社团','相结合','投入','选题','开展','高风险','严肃','整治','不端','地位',
    '加大','费用','加计','扣除','按照','使用','赋予','更大','路线','一般','灵活','一批','概念','验证','试验','首台','首批','次首','版次','力度','队伍','职务','单列',
    '具有','电报','解读','重磅',
    '为个','提供','金额','同日','共中个','中标','履行','产生','参保',
    '同等','权利','特大','镇同','专用','账户','基数','全体','每股','金红利','结算','清算','早期',
    '实体','严禁','违法','给予',
    '配额','累计','成交量','亿吨','成交额','举行','大会',
    '迎来','新一轮','景气','向上','性能','基于','持有','股占','尚未','双方','协商一致','解除','并于',
    '迈出','实质','步伐','千万','一致','第一季度','第二季度','第三季度','第四季度',
    '强烈','发表声明','遭遇','袭击','有人''进入','当局',
    '万余名','获悉','各方','加开','返程','班次','最后','一班','返回','为止','万余','申请','人形','启动','存在','阶段','同行','子公司','拟以','年度',
    '了解','时分','蓝色','今天','傍晚','明天','白天',
    '小时','目前','位列','第一','过往','头部','暂居','一笔','明明','直线','距离','公里','此事','出行','指出','当前','第一位',
    '坚决','果断','应转','转应','研的','一款','通用型','具备','不会','任何','周日','新闻联播','要闻','条月',
    '重量','不及','一张','纸财','日前','发表','最新','研究成果','还要','这个','包括','无需','悲观','认为','自月','下旬','经历',
    '处于','阶段性','问及','是否','参加','定于','从而','受访者','一艘','此外','已任','两年','之后','再度','履新',
    '之间','介绍','正式','显著','仍然','年底','架飞机','由不得','低于','第二次','这是','体现','一方面','对于',
    '通知','丰富','创板','标的','亿逆','周一','周五','三月','日有','四月','还有','日月','共有','陆续',
    '扩容','生效','南向','通共','调入','来自','发行人','北向','股通','十个','工作日','一轮','第六个',
    '元吨','年超','特别','四期','本期','固定','附息债','票面','计息','每半年','一次',
    '这些','大量','二季度','母公司','周二','率先','历程','第届','晚点',
    '周四','晚间','收盘','CM','比安已','为强','下半夜','登陆''位于','北纬度','东经','就是','东南','风力','西偏','北方','移动','强度','略有',
    '七下','八上','遏制','盯紧','看牢','部位','紧盯','多灾','易灾','重点部位','消除','户外','作业','逐一','点位','访问','启程','前往',
    '必要','召集','省份','会商','以后','多线','切实做好','防守','极端','四级','三级','通常','需要','特殊',
    '拧紧','化解','作为','时时','放心不下','事事','一个','著名','期刊','The','再次','遭到','四次','两次','指责',
    '该项','突破性','凌晨','总产量','三分之一','总产值','达成','临时性','请问','我要',
    '宣言','第五条','无人','岛礁''拖走','该舰','原状','第二','如菲','补给','出发','事先','通报','核查','运补','全过程','予以','第三','运送','上舰','试图',
    '近来','同菲方','磋商','双方同意','通电话','祝贺','第三天','超千','航班','当天',
    '自年','一份','一封信','他本','打算','寻求','为了','最佳','准备','一名','不久','评论',
    '本能','反应','一切','悬而未决','可能','至少','意味着','总体而言','暂时',
    '随着','季报','季度末','持仓','浮出','水面','普遍','仓位','三季度','多位','多个',
    '听取','汇报','何去何从','放弃','应该','能够','实质性','那么','应当','波动','下去','然而','获胜','不可避免','占据','上风',
    '写道','替换','重新','胜算','动摇','不过','不太可能','有太大','变动','达港','任命''密集','外界','卸载','燃料',
    '明确','简化','学会','专委会','不仅','展现','出超','灵活性','有效性','而且','坚实','最早',
    '大约','万个','已有','相当''万美元','上个月','大举','耗尽','或现','将成','线索','上周','延续','外部','内部','绩优','与此同时','半年报',
    '登上','时代','杂志','入画','登出','暂停','现货','早盘','走高','突破','盎司','日内涨','支持率','上升','百分点','百亿','使出','今年以来','加仓','手握','重金','愈发','排排',
    '升至','单周','超个','周度','额站','当下','基本面','低位','近几年','不断','许多','发出','这种','疑问','再次出现','回升','艰难','时刻','过去','升温','从中',
    '深耕','试验田','开市','五周年','承载','自立自强','使命','生产力','背景','下科','参与者','把握','自身',
    '被动','齐发','精准','自年科','投身','月末','并且','一季模态','日趋','成熟','爆发','大幅','值得','帐为','亿纽元','前值','投债','高财','一只','百亿元','来政金',
    '创下','阵营','诸多','钟爱','工具','热门','吸金','联接','大牌','外援','增幅','注入','场外','近年来','迅速','除了','之外','新发','亮点','业内','加剧','增长点',
    '大力','给出','天来','受欢迎','必争','逐渐','竞争','演变','比拼','推出''级别','才能','如今','以内','鲜见','攀升','预喜','预喜财',
    '含权','提速','在此期间','照进','现实','不可或缺','一年期','次日','纽约','场内',
    '多名','下属','派别','适合','新规','今起','新规于','三大','日起','卖出','两者','展期','九成','两市','压降','借方',
    '受让方','本金','亿亿亿','前天','出口','进口','开盘','综指','下跌','即日起','为财','从即日起','由此','低点',
    '沟通','余额','至约','创出','最近','新低','日常','增广','容大','录得','大型','多数','预测','几年','巨额','失效','多种','十几年','较强',
    '设定','较前','耗资','跌至',
    '这', '那', '这个', '那个', '这些', '那些', '什么', '谁', '哪', '哪个', '哪些', '怎么', '怎样', '为什么',
    '如何', '何时', '何地', '何人', '何物', '多少', '多长', '多大', '多高', '几时', '几天', '几个', '几何',
    '从', '到', '向', '往', '在于', '对于', '关于', '由于', '因为', '所以', '因此', '于是', '故而', '虽然',
    '尽管', '然而', '但是', '不过', '可是', '况且', '并且', '而且', '不仅', '除了', '另外', '此外', '再说',
    '总之', '总而言之', '归根结底', '之', '乎', '于', '其', '且', '若', '若是', '倘若', '假如', '假使', '假若', '倘使', '要是',
    '譬如', '像', '好像', '如同', '似乎', '般', '一般', '大约', '大概', '或许', '也许', '兴许',
    '多么', '这么', '那么', '如此', '颇', '颇为', '极', '极为', '甚', '甚为', '格外', '分外',
    '更加', '更为', '越发', '愈加', '愈发', '越来越', '渐渐', '逐渐', '日益', '越来越',
    '能', '可以', '可能', '或者', '或', '抑或', '还是', '莫非', '难道', '岂', '居然', '竟然',
    '反而', '却', '倒', '反倒', '反之', '可', '却是', '确是', '的确', '实在', '简直',
    '毕竟', '终究', '终于', '总算', '究竟', '到底', '终归', '终久', '终归', '到头来',
    '凡是', '凡', '所有', '一切', '每个', '每', '各个', '各', '任何', '所有的',
    '某', '某个', '某些', '某种', '有的', '有些', '之一', '之二', '之三',
    '曾', '曾经', '已', '已经', '刚才', '刚刚', '马上', '立刻', '立即', '随即', '即刻',
    '方才', '方', '才', '一直', '一向', '始终', '总是', '经常', '时常', '常常', '往往',
    '自从', '随着', '关于', '至于', '致', '对', '对于', '而言', '来说', '而言',
    '而已', '罢了', '着', '看', '据', '据此', '按', '按照', '依据', '依照', '根据',
    '以', '以便', '以免', '以至', '以至于', '与其', '宁可', '宁愿', '宁肯', '不如',
    '无论', '不管', '不论', '或是', '不是', '非', '并非', '毫无', '绝非', '决非',
    '顿时', '一下子', '霎时', '刹那间', '瞬间', '即', '就', '便', '才', '再', '又',
    '虽', '固然', '尽管如此', '即使', '哪怕', '纵然', '纵使', '如果说',
    '说起', '说到', '说来', '毫无疑问', '无疑', '诚然', '显然', '明显', '必然', '当然',
    '事实上', '实际上', '恰恰相反', '相反', '反过来说', '换句话说', '也就是说',
    '换言之', '总的来说', '总的来看', '总的说来', '严格地说', '具体地说',
    '具体来说', '简言之', '一般来说', '笼统地说', '宽泛地说', '整体上看', '整体而言',
    '一', '二', '三', '四', '五', '六', '七', '八', '九', '十', '百', '千', '万', '亿',
    '第一', '第二', '第三', '第四', '第五', '第六', '第七', '第八', '第九', '第十',
    '1', '2', '3', '4', '5', '6', '7', '8', '9', '0',
    '个', '位', '次', '番', '度', '回', '边', '遍', '下', '场', '趟', '回', '遭', '些',
    '们', '吧', '呢', '啊', '嘛', '哇', '呀', '哦', '唉', '哎', '喂', '嗯', '哼','上周五','上周四','上周三','上周二','上周一','上周六','上周日',
    '支持', '行业', '推荐', '推进','主题','据悉','打造','深度','加快','加强','提升','提高','推动','推出','推广','推进', '逐步', '构建', '实施','项目',
    '强化', '促进', '深度', '活跃','响应','提出','召开','意见','主要','第三家','第二家','第一家','第四家','第五家','恢复','业务','提交','代表','发布会',
    '涨近','系列','合同','合作','合理','合格','合法','社会','打造','培育','此前','完善','会议','据悉','造成','重要','更新','行动','情况','综合','毫米','厘米'
    ,'红色','蓝色','绿色','黄色','紫色','行动','情况','综合','集体','集团','商品','工程','日报','健全','签订','东方','计划','组织','未来','成交','公顷','公里',
    '控件','空间'
])