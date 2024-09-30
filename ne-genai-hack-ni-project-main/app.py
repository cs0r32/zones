import streamlit as st

def render(content,st):
    for item in content:
        print(item)
        if item["Type"] == "Title":
            st.markdown("## {}".format(item["Text"].strip(' ')))
        elif item["Type"] == "Section":
            st.markdown("**{}**".format(item["Text"].strip(' ')))
        elif item["Type"] == "Table":
            table_data = item["Text"]
            count = len(table_data)
            for index in range(0,count):
                for titems in table_data[index]:
                    if titems["Type"] == "Header":
                        st.markdown("**{}**".format(titems["Text"].strip(' ')))
                    else :
                        st.markdown("* {}".format(titems["Text"]))
        else:
            st.markdown(item["Text"])