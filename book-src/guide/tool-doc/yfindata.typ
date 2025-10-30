#import "/book.typ":book-page

#show: book-page.with(title: "yFinData CLI 工具")

#heading[
  #strong[yFinData CLI 工具]
]

#heading[yFinData 是什么？]

yFinData 是一个命令行界面（CLI）工具，可以帮助您捕获、管理和更新金融数据，包括股票价格和国家债务信息（通过国债收益率代理）。该工具使用 yfinance 来检索数据，并根据可配置的 TOML 文件将其存储在 SQLite 数据库中。

此工具是 QuanTrade 项目的一部分，旨在通过允许用户跟踪和更新特定股票和债务工具而无需重复手动下载大量数据集来提高金融数据管理的效率。


#heading[使用流程]

使用 yFinData 的典型工作流程包括以下几个关键步骤：

#heading[命令示例]

#strong[init] - 用数据库和配置文件初始化数据目录

#context[
  ```bash
  yFinData init data
  ```
]

此命令创建一个名为 `data` 的新目录，并在其中创建 `stock.db`（SQLite 数据库）和 `stock.toml`（配置文件）。

#strong[config] - 设置 TOML 和数据库文件的路径

#context[
  ```bash
  yFinData config --toml data/stock.toml --db data/stock.db
  ```
]

这将配置 yFinData 以在后续操作中使用指定的文件。

#strong[add] - 向配置中添加新股票或更新现有股票

#context[
  ```bash
  yFinData add AAPL 2023-01-01
  ```
]

此命令将苹果公司（AAPL）添加到您的配置中，从 2023 年 1 月 1 日开始。如果配置中已存在 AAPL，则更新开始日期。命令在更新配置后自动捕获数据。

#strong[update] - 更新现有数据到最新可用数据

#context[
  ```bash
  yFinData update
  ```
]

此命令通过仅下载缺失数据来高效更新您的数据库 - 数据库中存在但尚未达到当前日期的数据。这比每次都重新下载所有数据要高效得多。


#strong[download] - 根据配置下载数据

#context[
  ```bash
  yFinData download
  ```
]

此命令读取您的 TOML 配置并下载所有指定的股票和国家债务工具，并将其存储在您配置的数据库中。


#heading[配置文件]

// #v(0.3em)

TOML 配置文件定义了要跟踪的金融工具。以下是一个示例结构：

#context[
  ```toml
  [[stocks]]
  name = "AAPL"
  start_date = "2023-01-01"
  end_date = "2023-12-31"

  [[stocks]]
  name = "TSLA"
  start_date = "2023-01-01"
  end_date = "2023-12-31"

  [[national_debt]]
  name = "DGS10"
  start_date = "2023-01-01"
  end_date = "2023-12-31"
  ```
]

当您使用 `yFinData add` 时，它会自动使用新工具更新此配置文件。

// #h(0.8em)

// #heading[主要优势]

// #v(0.3em)

// #list(
//   #item[#strong[高效性]: 更新命令仅下载缺失数据，不重新下载现有信息。],
//   #item[#strong[配置驱动]: 在简单的 TOML 文件中定义要跟踪的内容。],
//   #item[#strong[本地存储]: 所有数据都存储在本地 SQLite 数据库中以实现快速访问。],
//   #item[#strong[易于管理]: 使用简单 CLI 命令添加、更新和维护您的金融数据集。]
// )
