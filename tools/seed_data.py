"""(Superseded: later hand-edits were made to data/apps.json, so do not re-run this.) ONE-TIME seed script that wrote data/apps.json. After this, edit data/apps.json directly.
(Kept in the repo only so the first research pass is reproducible.)"""
import json, pathlib
CHECKED = "2026-10-31"

S = {  # reusable sources
 "openai_fin": ("OpenAI Help: Finances in ChatGPT", "https://help.openai.com/en/articles/20001222-finances-in-chatgpt", "vendor"),
 "openai_ann": ("OpenAI: ChatGPT for personal finance", "https://openai.com/index/personal-finance-chatgpt/", "vendor"),
 "plaid_openai": ("Plaid: OpenAI customer story", "https://plaid.com/customer-stories/openai/", "vendor"),
 "grok_fin": ("Grokati: summary of the official @bot Finance announcement (Sep 26, 2026)", "https://www.grokati.com/articles/2026-09-26-grok-bot-finance-integration", "third-party"),
 "grok_pymnts": ("PYMNTS: Grok Puts the AI Assistant Between Consumers and Their Banks (Sep 28, 2026)", "https://www.pymnts.com/artificial-intelligence-2/2026/grok-puts-the-ai-assistant-between-consumers-and-their-banks/", "third-party"),
 "claude_money": ("BleepingComputer: Anthropic testing 'Claude Money' (Sep 16, 2026)", "https://www.bleepingcomputer.com/news/artificial-intelligence/anthropic-wants-claude-to-analyze-your-bank-account-and-financial-data/", "third-party"),
 "candor_chase": ("Candor: Is Chase blocking AI agents? (updated Oct 23, 2026; secondary reporting of CNBC/FT)", "https://candor.money/chase-blocking-ai-agents", "third-party"),
 "truthifi_guides": ("Truthifi: connect guides (vendor-reported coverage)", "https://truthifi.com/connect-hubs/connect-guides", "third-party"),
 "truthifi_chatgpt": ("Truthifi: ChatGPT + Fidelity page", "https://truthifi.com/connect/chatgpt-fidelity", "third-party"),
}
def src(*keys, extra=()):
    out=[{"label":S[k][0],"url":S[k][1],"type":S[k][2]} for k in keys]
    out += [{"label":l,"url":u,"type":t} for (l,u,t) in extra]
    return out
def p(status, how, conf="documented"): return {"status":status,"how":how,"confidence":conf}
def plaid_page(slug,name): return (f"Plaid: {name} institution page (lists supported Plaid products)", f"https://plaid.com/institutions/{slug}/", "vendor")

PLAID_CHATGPT = "ChatGPT Finances (built in, powered by Plaid, US only). Read-only."
GROK_FIN = "Grok Bot 'Finance' integration (Plaid, read-only) announced Sep 26, 2026. No supported-institution list published."
CLAUDE_NONE = "No first-party Claude bank-linking feature has launched ('Claude Money' was only spotted in testing). Only third-party connectors."

def bank(slug, name, plaid_slug, note, issues, extra_sources=(), chat_status="yes", chat_conf="inferred", chat_how=None, third_party_only=False, access_note="Read-only through ChatGPT Finances and Grok Finance. Neither can move money or pay bills."):
    return {
     "slug":slug,"name":name,"category":"Bank / card",
     "summary":note,
     "platforms":{
       "chatgpt":p(chat_status, chat_how or PLAID_CHATGPT, chat_conf),
       "claude":p("partial","No official Claude connector for this institution. Reachable only via third-party connectors such as Truthifi (vendor-reported coverage).","third-party-claim"),
       "grok":p("partial", GROK_FIN, "reported"),
     },
     "access":"read-only","access_note":access_note,
     "route":"Platform feature (Plaid)","issues":issues,
     "sources":src("openai_fin","grok_fin","truthifi_guides", extra=([plaid_page(plaid_slug,name)] if plaid_slug else [])+list(extra_sources)),
    }

apps=[]
# ---------------- Brokerages / crypto ----------------
apps.append({"slug":"robinhood","name":"Robinhood","category":"Brokerage","route":"Official MCP / agent connector",
 "summary":"Robinhood has an official 'Agentic' setup that lets an outside AI agent trade through a dedicated account.",
 "platforms":{"chatgpt":p("yes","Official external-agent onboarding; connect as a custom MCP connector."),
              "claude":p("yes","Official external-agent onboarding; connect as a custom MCP connector."),
              "grok":p("yes","Listed by Robinhood as a supported agent platform.")},
 "access":"can-trade","access_note":"The agent can place trades, but only inside the dedicated Agentic account you fund. Robinhood's docs say the agent can read your other accounts.",
 "issues":["Trading is limited to the separate Agentic account; read access spans your other accounts, so review what you share.","Requires an eligible Robinhood account; check Robinhood's page for current availability."],
 "sources":[{"label":"Robinhood Support: Onboarding an external agent","url":"https://robinhood.com/us/en/support/articles/onboarding-an-external-agent/","type":"vendor"},
            {"label":"Robinhood Support: Trading with your agent","url":"https://robinhood.com/us/en/support/articles/trading-with-your-agent/","type":"vendor"}]})
apps.append({"slug":"interactive-brokers","name":"Interactive Brokers (IBKR)","category":"Brokerage","route":"Official MCP / AI integrations",
 "summary":"IBKR publishes an AI Integrations page covering ChatGPT, Claude and Grok, with a standard mode and an opt-in autonomous mode.",
 "platforms":{"chatgpt":p("yes","Listed on IBKR's AI integrations page."),"claude":p("yes","Listed on IBKR's AI integrations page."),"grok":p("yes","Listed on IBKR's AI integrations page.")},
 "access":"draft-trades","access_note":"Standard mode: the AI drafts order instructions and you submit them. IBKR also describes an autonomous-trading option for eligible accounts.",
 "issues":["Autonomous trading is opt-in and eligibility-based; confirm which mode your account is in.","Availability varies by country; this site covers US users."],
 "sources":[{"label":"IBKR: AI integrations","url":"https://www.interactivebrokers.com/en/trading/ai-integrations.php","type":"vendor"}]})
apps.append({"slug":"public","name":"Public.com","category":"Brokerage","route":"Official hosted MCP",
 "summary":"Public offers a hosted MCP server that works with the big chat assistants and can place real orders.",
 "platforms":{"chatgpt":p("yes","Hosted MCP; add as a custom connector."),"claude":p("yes","Hosted MCP; add as a custom connector."),"grok":p("yes","Hosted MCP; add as a custom connector.")},
 "access":"can-trade","access_note":"The MCP server can place real orders. Treat it like handing someone your trading screen.",
 "issues":["No separate sandbox account is documented on the hosted-MCP page; check Public's docs for order limits and confirmation settings."],
 "sources":[{"label":"Public API docs: hosted MCP","url":"https://public.com/api/docs/templates/hosted-mcp","type":"vendor"}]})
apps.append({"slug":"webull","name":"Webull","category":"Brokerage","route":"Official cloud MCP",
 "summary":"Webull's developer docs describe a cloud MCP server usable from ChatGPT, Claude and Grok.",
 "platforms":{"chatgpt":p("yes","Webull docs say it can be operated from ChatGPT."),"claude":p("yes","Webull docs say it can be operated from Claude."),"grok":p("yes","Webull docs say it can be operated from Grok.")},
 "access":"draft-trades","access_note":"Per Webull's docs, trade instructions created by the AI must be confirmed in the Webull app before they execute.",
 "issues":["Requires Webull developer/API access to be enabled on your account.","Docs also describe a community-posting tool; check which tools you enable."],
 "sources":[{"label":"Webull Developer: MCP","url":"https://developer.webull.com/apis/docs/AI-friendly-Resources/mcp/","type":"vendor"}]})
apps.append({"slug":"coinbase","name":"Coinbase","category":"Crypto exchange","route":"Official 'Coinbase for Agents'",
 "summary":"Coinbase documents an agents toolkit covering ChatGPT, Claude and Grok, with portfolio scoping to limit what an agent can touch.",
 "platforms":{"chatgpt":p("yes","Listed in Coinbase for Agents docs."),"claude":p("yes","Listed in Coinbase for Agents docs."),"grok":p("yes","Listed in Coinbase for Agents docs.")},
 "access":"can-trade","access_note":"Agents can trade and convert crypto. Coinbase documents scoping an agent to a specific portfolio so it can't touch the rest.",
 "issues":["Use a dedicated, limited portfolio rather than your main one."],
 "sources":[{"label":"Coinbase Developer Docs: Coinbase for Agents","url":"https://docs.cdp.coinbase.com/coinbase-for-agents/overview","type":"vendor"}]})
apps.append({"slug":"tastytrade","name":"tastytrade","category":"Brokerage","route":"Official open-source MCP (self-hosted)",
 "summary":"tastytrade publishes an official MCP server, but you run it yourself on your own computer. It is not a one-click connector.",
 "platforms":{"chatgpt":p("unknown","tastytrade's pages do not list ChatGPT. A locally-run (stdio) server generally can't be added to ChatGPT's web app without extra hosting.","absence-of-docs"),
              "claude":p("partial","Self-hosted local server; works with MCP clients that can run local servers (for example Claude Desktop/Code). tastytrade's pages don't name Claude specifically.","inferred"),
              "grok":p("unknown","Not listed on tastytrade's pages.","absence-of-docs")},
 "access":"can-trade","access_note":"The server can place orders. tastytrade's docs describe a dry-run option for testing.",
 "issues":["Developer-style setup (install, API credentials).","No hosted consumer connector documented."],
 "sources":[{"label":"tastytrade: MCP server","url":"https://tastytrade.com/mcp-server/","type":"vendor"},{"label":"tastytrade Developer docs: MCP server","url":"https://developer.tastytrade.com/docs/sdks-and-tools/mcp-server/","type":"vendor"}]})
apps.append({"slug":"alpaca","name":"Alpaca","category":"Brokerage (API-first)","route":"Official open-source MCP (self-hosted)",
 "summary":"Alpaca's official MCP server runs locally with your API keys. Defaults to paper trading.",
 "platforms":{"chatgpt":p("partial","Docs mention ChatGPT only as 'see the README'; no hosted connector documented.","inferred"),
              "claude":p("yes","Claude Desktop and Claude Code are listed supported clients (local or remote).")  ,
              "grok":p("unknown","Not listed in Alpaca's supported-client table.","absence-of-docs")},
 "access":"can-trade","access_note":"65 tools including placing orders, closing all positions and cancelling orders. Paper trading is the default; live trading needs ALPACA_PAPER_TRADE=false.",
 "issues":["You paste API keys into a local config, never into chat.","Toolsets can be limited (for example account + market data only) to make it read-only."],
 "sources":[{"label":"Alpaca Docs: Trading API MCP","url":"https://docs.alpaca.markets/us/docs/trading-api-mcp","type":"vendor"},{"label":"GitHub: alpacahq/alpaca-mcp-server","url":"https://github.com/alpacahq/alpaca-mcp-server","type":"vendor"}]})
apps.append({"slug":"charles-schwab","name":"Charles Schwab","category":"Brokerage","route":"Pilot (Claude), third-party",
 "summary":"Schwab says it is piloting an official MCP connection for traders, starting with Claude. Today there is no public self-serve connector.",
 "platforms":{"chatgpt":p("unknown","No Schwab connector announced for ChatGPT. Whether ChatGPT Finances can link Schwab via Plaid was not verified here; check the connect screen.","absence-of-docs"),
              "claude":p("partial","Schwab's CEO described an invite-style pilot letting traders connect their own model, starting with Claude (Oct 15, 2026 earnings call, as reported). Community-built MCP servers and Truthifi also exist.","reported"),
              "grok":p("unknown","No Schwab connector announced for Grok.","absence-of-docs")},
 "access":"read-only","access_note":"The CEO said connected models cannot move money. Community-built servers that use Schwab's Trader API can place orders and are not endorsed by Schwab.",
 "issues":["Pilot permissions have not been published.","Schwab says it blocks AI agents that log in with a client's username and password.","Community MCP servers need your own Schwab developer app and are unofficial."],
 "sources":[{"label":"WallStreetDebug: Schwab blocks unauthorized AI agents, pilots Claude MCP access (Oct 16-22, 2026; cites SEC filing and earnings call)","url":"https://wallstreetdebug.com/articles/schwab-blocks-unauthorized-ai-agents-mcp-pilot-claude/","type":"third-party"},
          {"label":"Truthifi: Schwab MCP","url":"https://truthifi.com/providermcps/schwab-mcp","type":"third-party"},
          {"label":"Candor: Chase/Schwab agent blocking roundup","url":"https://candor.money/chase-blocking-ai-agents","type":"third-party"}]})
apps.append({"slug":"fidelity","name":"Fidelity","category":"Brokerage","route":"No official route; third-party only",
 "summary":"Fidelity has not published an official AI connector. A Fidelity staff reply says there is no public API or MCP. Third-party read-only tools exist.",
 "platforms":{"chatgpt":p("partial","Third-party only (Truthifi, Synci, BankBridge). Whether ChatGPT Finances links Fidelity via Plaid was not verified here.","third-party-claim"),
              "claude":p("partial","Third-party only (Truthifi, Synci, BankBridge).","third-party-claim"),
              "grok":p("partial","Third-party only; Truthifi lists Grok guides.","third-party-claim")},
 "access":"read-only","access_note":"The third-party tools found describe read-only access. Fidelity itself provides none.",
 "issues":["Fidelity staff statement (Reddit) says no public API/MCP; a staff statement is not a formal policy page.","Truthifi's pages disagree on which ChatGPT plans are required.","Fidelity accounts linked through Finicity are excluded from Monarch's MCP."],
 "sources":[{"label":"Fidelity staff reply on r/fidelityinvestments","url":"https://www.reddit.com/r/fidelityinvestments/comments/1o8la8b/mcp_andor_apis/","type":"vendor-staff"},
            {"label":"Truthifi: ChatGPT + Fidelity","url":"https://truthifi.com/connect/chatgpt-fidelity","type":"third-party"},
            {"label":"Synci: Fidelity MCP","url":"https://synci.io/brokerages/us-fidelity/mcp","type":"third-party"},
            {"label":"BankBridge: Fidelity","url":"https://bankbridge.money/banks/fidelity","type":"third-party"},
            {"label":"Monarch Help: MCP connector (Finicity exclusion)","url":"https://help.monarch.com/hc/en-us/articles/50207234679956-Monarch-MCP-Connector","type":"vendor"}]})
apps.append({"slug":"vanguard","name":"Vanguard","category":"Brokerage","route":"Platform feature (Plaid); third-party",
 "summary":"Plaid lists Vanguard with investments data, so ChatGPT Finances and Grok Finance should be able to read it. Vanguard has no AI connector of its own.",
 "platforms":{"chatgpt":p("yes",PLAID_CHATGPT+" Plaid's Vanguard page lists Investments support.","inferred"),
              "claude":p("partial","No official connector; Truthifi lists Vanguard (vendor-reported).","third-party-claim"),
              "grok":p("partial",GROK_FIN,"reported")},
 "access":"read-only","access_note":"Read-only. Neither ChatGPT Finances nor Grok Finance can place trades.",
 "issues":["Status is inferred from Plaid's coverage page plus OpenAI/xAI statements. Neither OpenAI nor xAI publishes a per-institution list."],
 "sources":src("openai_fin","grok_fin","truthifi_guides",extra=[plaid_page("vanguard","Vanguard")])})

# ---------------- Banks ----------------
apps.append(bank("chase","Chase","", "Chase says it supports customer-approved data sharing through providers like Plaid, but blocks AI agents that log in with your password.",
 ["JPMorgan said in Oct 2026 it blocks outside AI agents that sign in with a customer's credentials (as reported by CNBC/FT via Candor).","A renewed Chase-Plaid data agreement was announced Sep 16, 2025.","Chase's own Linked apps page lets you see and revoke connections."],
 extra_sources=[("JPMorganChase: renewed Plaid data access agreement (Sep 16, 2025)","https://media.chase.com/news/jpmorganchase-plaid-extend-data-access-agreement","vendor"),("Candor: Is Chase blocking AI agents?","https://candor.money/chase-blocking-ai-agents","third-party")]))
apps.append(bank("bank-of-america","Bank of America","bank-of-america","Plaid lists Bank of America (balances and transactions; no investments product listed). Reported to be limiting AI agents that log in as the customer.",
 ["Financial Times reported (Oct 16, 2026, via Candor) that Bank of America is limiting AI agents' access to accounts.","Plaid's page lists Assets, Auth, Balance and Transactions; Investments not listed."]))
apps.append(bank("wells-fargo","Wells Fargo","wells-fargo","Plaid lists Wells Fargo including Investments. No Wells Fargo-specific AI connector found.",
 ["No Wells Fargo statement about AI agents found."]))
apps.append(bank("capital-one","Capital One","","No Capital One AI connector found. Coverage by ChatGPT/Grok through Plaid was not verified on a Plaid page.",
 ["Plaid institution page for Capital One was not found at the expected URL, so per-bank Plaid support is unverified."],chat_status="partial",chat_conf="inferred",
 chat_how="ChatGPT Finances connects 'over 12,000' US institutions through Plaid; Capital One was not individually confirmed."))
apps.append(bank("citi","Citi","","No Citi AI connector found. Reported to be restricting AI agents.",
 ["Financial Times reported (Oct 16, 2026, via Candor) that Citi is restricting AI agents' access to accounts.","Per-bank Plaid support not individually confirmed."],chat_status="partial",chat_conf="inferred",
 chat_how="ChatGPT Finances connects 'over 12,000' US institutions through Plaid; Citi was not individually confirmed.",extra_sources=[("Candor: Is Chase blocking AI agents? (mentions Citi/BofA)","https://candor.money/chase-blocking-ai-agents","third-party")]))
apps.append(bank("ally","Ally Bank","ally-bank","Plaid lists Ally (deposit accounts, balances, transactions). No Ally AI connector found.",
 ["Ally Invest (brokerage) is a separate product and was not checked."]))
apps.append(bank("american-express","American Express","american-express","Plaid lists American Express card and loan data (no investments). No Amex AI connector found.",
 ["Per-card coverage (for example business cards) not checked."]))
apps.append(bank("sofi","SoFi","","No SoFi AI connector found. ChatGPT/Grok coverage through Plaid not individually confirmed.",
 ["Plaid institution page for SoFi was not found at the expected URL; per-bank Plaid support is unverified."],chat_status="partial",chat_conf="inferred",
 chat_how="ChatGPT Finances connects 'over 12,000' US institutions through Plaid; SoFi was not individually confirmed."))

# ---------------- Budgeting apps ----------------
apps.append({"slug":"monarch-money","name":"Monarch Money","category":"Budgeting app","route":"Official MCP connector",
 "summary":"Monarch has an official MCP connector for ChatGPT and Claude. Read access by default, with optional write access.",
 "platforms":{"chatgpt":p("yes","Official connector; Monarch's help page says ChatGPT web, on plans that support custom connectors."),
              "claude":p("yes","Official connector listed on Monarch's help page."),
              "grok":p("partial","Not listed as supported by Monarch. Remote MCP clients may accept the same URL, but this is not officially supported.","inferred")},
 "access":"read-edit","access_note":"Reads by default. Monarch describes an optional setting that lets the AI make changes in your Monarch data.",
 "issues":["Accounts connected through Finicity are excluded from the MCP, which affects some Fidelity and other investment accounts.","Keep write access off unless you need it."],
 "sources":[{"label":"Monarch Help: MCP connector","url":"https://help.monarch.com/hc/en-us/articles/50207234679956-Monarch-MCP-Connector","type":"vendor"}]})
apps.append({"slug":"copilot-money","name":"Copilot Money","category":"Budgeting app","route":"Official MCP (beta)",
 "summary":"Copilot has an official read-only MCP for ChatGPT and Claude. Grok is not on its list.",
 "platforms":{"chatgpt":p("yes","Listed on Copilot's MCP setup page."),"claude":p("yes","Listed on Copilot's MCP setup page."),
              "grok":p("unknown","Grok is not on Copilot's supported list; not tested.","absence-of-docs")},
 "access":"read-only","access_note":"Copilot describes the MCP as read-only.",
 "issues":["Copilot's help article calls the feature beta; features may change."],
 "sources":[{"label":"Copilot Help: Setting up the MCP","url":"https://help.copilot.money/en/articles/14758080-setting-up-the-mcp","type":"vendor"},{"label":"Copilot: MCP","url":"https://www.copilot.money/mcp","type":"vendor"}]})
apps.append({"slug":"ynab","name":"YNAB","category":"Budgeting app","route":"Third-party MCP only",
 "summary":"YNAB's official ChatGPT app gives budgeting guidance but cannot see your plan. Live-data access only through third-party MCP servers.",
 "platforms":{"chatgpt":p("partial","Official YNAB app in ChatGPT is advice-only and can't see your plan. Third-party MCP servers can.","documented"),
              "claude":p("partial","No official YNAB MCP found. Third-party MCP servers exist (use your own API token).","third-party-claim"),
              "grok":p("unknown","Nothing found.","absence-of-docs")},
 "access":"read-edit","access_note":"The official ChatGPT app has no access to your data. Third-party MCP servers can typically read and edit your budget.",
 "issues":["Third-party servers need a YNAB personal access token. You are trusting that server's author with it.","Verify any third-party server's code before use."],
 "sources":[{"label":"YNAB Support: YNAB and ChatGPT","url":"https://support.ynab.com/en_us/ynab-and-chatgpt-H1QI25JRZe.md","type":"vendor"}]})
apps.append({"slug":"rocket-money","name":"Rocket Money","category":"Budgeting app","route":"None found",
 "summary":"No official Rocket Money connector for any chat assistant found. Users are asking for one on its feedback board.",
 "platforms":{"chatgpt":p("no","No official connector found.","absence-of-docs"),"claude":p("no","No official connector found.","absence-of-docs"),"grok":p("no","No official connector found.","absence-of-docs")},
 "access":"none","access_note":"Nothing to connect. You can still export data and upload it yourself, which has privacy tradeoffs.",
 "issues":["'No' here means 'no official support found as of the checked date', based on the absence of docs plus an open feature request."],
 "sources":[{"label":"Rocket Money feedback board: Add MCP / AI agent connector (open request)","url":"https://rocketmoney.canny.io/feature-requests-for-web/p/add-mcp-ai-agent-connector-read-only","type":"vendor"}]})
apps.append({"slug":"origin","name":"Origin","category":"Budgeting app","route":"None (own AI advisor)",
 "summary":"Origin has its own built-in AI advisor. Staff replies say it does not offer connections to outside assistants.",
 "platforms":{"chatgpt":p("no","Staff say no external-assistant connection.","vendor-staff-statement"),"claude":p("no","Staff say no external-assistant connection.","vendor-staff-statement"),"grok":p("no","Staff say no external-assistant connection.","vendor-staff-statement")},
 "access":"none","access_note":"Nothing to connect. Origin's own AI Advisor works inside the app.",
 "issues":["Based on staff replies on Reddit and a help page, not a formal policy; may change."],
 "sources":[{"label":"Origin Help: What LLMs does AI Advisor use?","url":"https://support.useorigin.com/hc/en-us/articles/39417044720397-What-LLM-s-does-AI-Advisor-use","type":"vendor"},{"label":"r/OriginFinancial staff replies","url":"https://www.reddit.com/r/OriginFinancial/","type":"vendor-staff"}]})

# ---------------- Aggregators / infrastructure ----------------
apps.append({"slug":"plaid","name":"Plaid","category":"Data aggregator","route":"Powers ChatGPT & Grok finance features",
 "summary":"Plaid is the pipe behind ChatGPT Finances and Grok's Finance integration. Its own Claude-compatible MCP is for developers, not for linking your accounts.",
 "platforms":{"chatgpt":p("yes","ChatGPT Finances uses Plaid. Read-only."),
              "claude":p("no","Plaid's remote Dashboard MCP exposes developer diagnostics (Link analytics, usage), not consumer bank data. No Claude consumer bank-linking feature has launched."),
              "grok":p("yes","Grok Bot's Finance integration connects through Plaid (read-only), per official @bot posts as reported.","reported")},
 "access":"read-only","access_note":"Consumer links through ChatGPT/Grok are read-only. The Dashboard MCP is for developers' own Plaid teams.",
 "issues":["Dashboard MCP is 'under active development' with limited support, per Plaid.","Banks control what they share; Chase and others have said they restrict credential-based agents but still support Plaid."],
 "sources":[{"label":"Plaid Docs: Dashboard MCP server","url":"https://plaid.com/docs/resources/mcp/","type":"vendor"}]+src("plaid_openai","grok_pymnts","claude_money")})
apps.append({"slug":"finicity-mastercard","name":"Finicity (Mastercard Open Finance)","category":"Data aggregator","route":"Developer-docs MCP only",
 "summary":"Mastercard's MCP serves developer documentation and API specs. It does not give an assistant your account data.",
 "platforms":{"chatgpt":p("no","No consumer-account MCP found.","absence-of-docs"),"claude":p("no","No consumer-account MCP found. Mastercard's MCP is documentation-only.","third-party-claim"),"grok":p("no","No consumer-account MCP found.","absence-of-docs")},
 "access":"none","access_note":"Docs-only MCP. No customer data via MCP.",
 "issues":["Finicity-sourced accounts are excluded from Monarch's MCP.","Description of the Mastercard MCP comes from a third-party directory; Mastercard's own page was not opened."],
 "sources":[{"label":"Mastercard Developers: Agent Toolkit","url":"https://developer.mastercard.com/platform/documentation/agent-toolkit/","type":"vendor"},{"label":"wealthtech.dev: Mastercard Developers Agent Toolkit (third-party summary)","url":"https://wealthtech.dev/mcp/finicity-agent-toolkit","type":"third-party"}]})
apps.append({"slug":"mx","name":"MX","category":"Data aggregator","route":"None found",
 "summary":"MX has written about AI agents, but no consumer-facing MCP or ChatGPT/Claude/Grok connector was found.",
 "platforms":{"chatgpt":p("no","No official connector found.","absence-of-docs"),"claude":p("no","No official connector found.","absence-of-docs"),"grok":p("no","No official connector found.","absence-of-docs")},
 "access":"none","access_note":"Nothing official to connect.",
 "issues":["Third-party services built on MX data exist; those are not MX connectors."],
 "sources":[{"label":"MX: Architecture of Action","url":"https://www.mx.com/news/architecture-of-action/","type":"vendor"}]})
apps.append({"slug":"truthifi","name":"Truthifi","category":"Third-party aggregator MCP","route":"Third-party hosted MCP",
 "summary":"Truthifi is a third-party service that links many US brokerages and banks and exposes them to Claude, ChatGPT and others through its own MCP.",
 "platforms":{"chatgpt":p("partial","Supported, but Truthifi's own pages disagree on required ChatGPT plans (Plus/Pro on one page; Business/Enterprise/Edu on another).","third-party-claim"),
              "claude":p("yes","Truthifi's guides list Claude (Pro, Max, Enterprise).","third-party-claim"),
              "grok":p("partial","Truthifi guide pages mention Grok; its main supported-assistants list does not.","third-party-claim")},
 "access":"read-only","access_note":"Truthifi describes read-only access. Coverage claims are the vendor's own.",
 "issues":["You are giving a third party read access to your accounts. Read its privacy terms.","Institution coverage is vendor-reported and not independently verified here."],
 "sources":src("truthifi_guides","truthifi_chatgpt")})

for a in apps:
    a["checked"]=CHECKED
    a["affiliate"]={"slot":True,"label":None,"url":None,"note":"TODO: add affiliate link here only if a program exists and Clay has signed up. Leave null until then."}
pathlib.Path("data").mkdir(exist_ok=True)
json.dump({"meta":{"site":"Plug Your Money In","generated_by":"tools/seed_data.py","status_values":["yes","partial","no","unknown"]},"apps":apps},open("data/apps.json","w"),indent=1,ensure_ascii=False)
print(len(apps))
