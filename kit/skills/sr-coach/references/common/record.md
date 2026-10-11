# 记录契约 v1

每条关键记录必须有：id、revision（正整数）、kind、statement、status、source、asOf、updatedAt、confirmedBy、reviewOn、supersedes、scope。Markdown 可用字段列表；JSON 同义。

- status：proposed / confirmed / disputed / superseded，描述事实或决定的确认状态。
- scope：public / synthetic / internal / private。用户个人背景不是公开资料，不能因模型可见而标 public。
- source：具体文件及版本、消息日期或可验证网址。未知值写 null 或“未知”，不编造确认人和截止日。
- asOf 是事实适用日期；updatedAt 是写入时间，均附时区。reviewOn 触发复核，不自动失效或删除。
- confirmedBy 只记录实际确认依据。用户明确陈述或已授权的行动直接记账；推测仍为 proposed。
- 来源有冲突时保留两方原文与版本，标 disputed；不按新旧自动裁决。
- 执行进展单独保存 implementation、engineeringValidation、scenarioValidation、adoption、effect，各为 not_started / in_progress / verified / unknown，并附证据；其中 verified 只说明该层有相应证据。
- 产物存在不等于效果确认；完成的软件测试不证明真实产品指标达标。
- 数值必须关联模型、输入版本、计算工具、命令和限制。
