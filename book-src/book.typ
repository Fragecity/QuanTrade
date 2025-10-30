
#import "@preview/shiroa:0.2.3": *
// #set text(font: "WenQuanYi Zen Hei")
#show: book

#book-meta(
  title: "小白理财书",
  description: "记录一个小白学习理财的点滴。",
  repository: "https://github.com/Fragecity/QuanTrade.git",
  authors: ("今日无更",),
  language: "zh",
  summary: [
    // = Prefix
    - #prefix-chapter("prefix.typ")[Prefix]
    = 金融扫盲
    // == 金融产品
    - #chapter("guide/terminology/金融产品.typ", section: "1")[金融产品]
      - #chapter("guide/terminology/债券.typ", section: "1.1")[债券]
      // - #chapter("guide/terminology/股票.typ", section: "1.2")[股票]
      - #chapter("guide/terminology/基金.typ", section: "1.2")[基金/ETF]
      - #chapter("guide/terminology/期权与期货.typ", section: "1.3")[期权与期货]
    // == 技术名词
    - #chapter("guide/terminology/技术名词.typ", section: "2")[技术名词]
      - #chapter("guide/terminology/量化.typ", section: "2.1")[量化]

    = 工具文档
    // == yfindata
    - #chapter("guide/tool-doc/yfindata.typ", section: "1")[yfindata]
  ]
)

#build-meta(dest-dir: "./dist")

// re-export page template
#import "/templates/page.typ": project, heading-reference
#let book-page = project
// #let cross-link = cross-link
#let heading-reference = heading-reference
