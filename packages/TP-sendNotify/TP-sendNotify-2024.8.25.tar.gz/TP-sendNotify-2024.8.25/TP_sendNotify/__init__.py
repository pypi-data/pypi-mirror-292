import json_duplicate_keys as jdks
import requests
import os


# Sending message notification to Discord channel
def toDiscord(bot_name, message, SidebarColor=None, ConfigFile=None):
	if type(bot_name) != str: bot_name = ""

	if type(ConfigFile) == str and len(ConfigFile) > 0:
		NotifyConf = jdks.load(ConfigFile)
	else:
		if not os.path.isfile(os.path.join(os.path.expanduser("~"), ".TPConfig", "sendNotify.json")):
			if not os.path.isdir(os.path.join(os.path.expanduser("~"), ".TPConfig")):
				os.mkdir(os.path.join(os.path.expanduser("~"), ".TPConfig"))
			jdks.JSON_DUPLICATE_KEYS({
				"Discord": {
					"BOT_NAME": {
						"webhook_url": "https://discord.com/api/webhooks/WEBHOOK_ID/WEBHOOK_TOKEN"
					}
				}
			}).dump(os.path.join(os.path.expanduser("~"), ".TPConfig", "sendNotify.json"), indent=4)

		NotifyConf = jdks.load(os.path.join(os.path.expanduser("~"), ".TPConfig", "sendNotify.json"))

	if NotifyConf:
		webhook_url = NotifyConf.get("Discord||"+bot_name+"||webhook_url")
		if type(webhook_url) == str and len(webhook_url) > 0:
			if type(message) == str and len(message) > 0:
				json_data = { "embeds": [ { "description": message }]}
				if type(SidebarColor) == int:
					json_data["embeds"][0]["color"] = SidebarColor

				try:
					requests.post(webhook_url, json=json_data)
				except Exception as e:
					pass