
#import "@preview/shiroa:0.2.3": *

#show: book

#book-meta(
  title: "小白理财书",
  description: "记录一个小白学习理财的点滴。",
  repository: "https://github.com/Fragecity/QuanTrade.git",
  authors: ("今日无更",),
  language: "zh",
  summary: [
    = Prefix
    - #prefix-chapter("sample-page.typ")[Hello, typst]
    = 金融扫盲
    - #chapter("guide/Introduction.typ", section: "1.1")[Introduction]
  ]
)



// re-export page template
#import "/templates/page.typ": project
#let book-page = project
