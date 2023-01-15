import json

def get_violations():
    filters= ["cat.aria", "cat.color", "cat.name-role-value", "cat.sensory-and-visual-cues", "cat.text-alternatives"]
    with open('a11.json', 'r') as f_in:
        data = json.load(f_in)


    results= []

    counter=0
    for x in data:
        tags= x["tags"]
        # print(tags)
        for filter in filters:
            # print(filter)
            if filter in tags:
              # if "cat.text-alternatives" in x["tags"] or "cat.aria" in  :
                desc=  x["description"]
                help= x["help"]
                helpUrl= x["helpUrl"]

                for y in x["nodes"]:
                    # print(y.keys())
                    for z in y.keys():
                        counter+=1
                        html_code= y["html"]
                        summary= y["failureSummary"]
                        break
                results.append({"issue": desc, "help": help, "help_url": helpUrl, "html_code": html_code, "summary": summary})

    return results
   
