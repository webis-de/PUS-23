from requests import get

documents = {"CRISPR_narrative-events.csv":{"key":"1wRwgRmMYluVJPrr_p-BKn6fycDGmZ_JdlI-5dWUKnMw",
                                            "gid":"1179906549",
                                            "output":"csv"},
             "CRISPR_publication-events.csv":{"key":"1wRwgRmMYluVJPrr_p-BKn6fycDGmZ_JdlI-5dWUKnMw",
                                              "gid":"1337994121",
                                              "output":"csv"},
             "CRISPR_publication-events-hochzitierte.csv":{"key":"1wRwgRmMYluVJPrr_p-BKn6fycDGmZ_JdlI-5dWUKnMw",
                                                       "gid":"1044799910",
                                                       "output":"csv"},
             "CRISPR_accounts.csv":{"key":"1wRwgRmMYluVJPrr_p-BKn6fycDGmZ_JdlI-5dWUKnMw",
                                    "gid":"1402599909",
                                    "output":"csv"},
             }

for filename,parameters in documents.items():
    with open(filename, "w") as file:
        content = get("https://docs.google.com/spreadsheet/ccc", params=parameters)
        file.write(content.text.encode("ISO-8859-1").decode("utf-8"))

