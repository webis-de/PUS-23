def prettyprint(structure, indent = ""):
    if structure and type(structure) == dict:
        return "\n".join([indent + str(pair[0]) + "\n" + prettyprint(pair[1], indent + "    ") for pair in structure.items()])
    elif structure and type(structure) == list:
        return "\n".join(prettyprint(item, indent) for item in structure)
    else:
        if structure:
            return indent + str(structure)
        else:
            return indent + "-"

if __name__ == "__main__":

    d = {"a":"a","b":[1,2,{3:3,"3":"3"}],"c":{1:1,"2":"2"}}

    print(prettyprint(d))
