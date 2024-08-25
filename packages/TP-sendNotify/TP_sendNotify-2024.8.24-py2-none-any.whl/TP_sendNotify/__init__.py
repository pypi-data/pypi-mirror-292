import json_duplicate_keys as jdks
import requests
import os


# Sending message notification to Discord channel
def toDiscord(message, SidebarColor=None, ConfigFile=None):
	if type(ConfigFile) == str and len(ConfigFile) > 0:
		NotifyConf = jdks.load(ConfigFile)
	else:
		if not os.path.isfile(os.path.join(os.path.expanduser("~"), ".TPConfig", "sendNotify.json")):
			if not os.path.isdir(os.path.join(os.path.expanduser("~"), ".TPConfig")):
				os.mkdir(os.path.join(os.path.expanduser("~"), ".TPConfig"))
			jdks.JSON_DUPLICATE_KEYS({
				"Discord": [
					{
						"webhook_url": ""
					}
				]
			}).dump(os.path.join(os.path.expanduser("~"), ".TPConfig", "sendNotify.json"), indent=4)

		NotifyConf = jdks.load(os.path.join(os.path.expanduser("~"), ".TPConfig", "sendNotify.json"))

	if NotifyConf and type(NotifyConf.get("Discord")) == list:
		for bot in NotifyConf.get("Discord"):
			if type(bot["webhook_url"]) == str and len(bot["webhook_url"]) > 0:
				json_data = { "embeds": [ { "description": message }]}
				if type(SidebarColor) == int:
					json_data["embeds"][0]["color"] = SidebarColor

				try:
					requests.post(bot["webhook_url"], json=json_data)
				except Exception as e:
					pass