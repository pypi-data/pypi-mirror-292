# TP-sendNotify

<p align="center">
    <a href="https://github.com/truocphan/TP-sendNotify/releases/"><img src="https://img.shields.io/github/release/truocphan/TP-sendNotify" height=30></a>
    <a href="#"><img src="https://img.shields.io/github/downloads/truocphan/TP-sendNotify/total" height=30></a>
    <a href="#"><img src="https://img.shields.io/github/stars/truocphan/TP-sendNotify" height=30></a>
    <a href="#"><img src="https://img.shields.io/github/forks/truocphan/TP-sendNotify" height=30></a>
    <a href="https://github.com/truocphan/TP-sendNotify/issues?q=is%3Aopen+is%3Aissue"><img src="https://img.shields.io/github/issues/truocphan/TP-sendNotify" height=30></a>
    <a href="https://github.com/truocphan/TP-sendNotify/issues?q=is%3Aissue+is%3Aclosed"><img src="https://img.shields.io/github/issues-closed/truocphan/TP-sendNotify" height=30></a>
</p>

## Installation
#### From PyPI:
```console
pip install TP-sendNotify
```
#### From Source:
```console
git clone https://github.com/truocphan/TP-sendNotify.git --branch <Branch/Tag>
cd TP-sendNotify
python setup.py build
python setup.py install
```

## Basic Usage
The default configuration file created at `~/.TPConfig/sendNotify.json` has the following content:
```json
{
    "Discord": {
        "BOT_NAME": {
            "webhook_url": "https://discord.com/api/webhooks/WEBHOOK_ID/WEBHOOK_TOKEN"
        },
        ...
    }
}
```

### toDiscord(bot_name, message, SidebarColor=None, ConfigFile=None)
Sending message notification to Discord channel
```python
import TP_sendNotify

TP_sendNotify.toDiscord("BOT_NAME", "This message notification has been sent to the Discord channel using TP-sendNotify", SidebarColor=13370624)
```