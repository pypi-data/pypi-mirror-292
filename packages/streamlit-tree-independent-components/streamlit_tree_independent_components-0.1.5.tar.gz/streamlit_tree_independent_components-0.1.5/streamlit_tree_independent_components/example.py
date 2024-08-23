import streamlit as st
from streamlit_tree_independent_components import tree_independent_components


st.subheader("Component with input args")


treeItems = {
   "id":"0",
   "name":"Project Dashboard",
   "icon":"folder",
   "disable":False,
   "children":[
      {
         "id":"1",
         "name":"Technology Expense Summary",
         "icon":"document",
         "disable":False,
         "children":[
            {
               "id":"2",
               "name":"Cost Efficiency Analysis",
               "icon":"document",
               "disable":False,
               "children":[
                  {
                     "id":"3",
                     "name":"Financial Data Preparation",
                     "icon":"document",
                     "disable":False
                  },
                  {
                     "id":"4",
                     "name":"Database Operations Review",
                     "icon":"document",
                     "disable":False,
                     "children":[
                        {
                           "id":"5",
                           "name":"Data Entry for Operations",
                           "icon":"document",
                           "disable":False,
                           "children":[
                              {
                                 "id":"6",
                                 "name":"User Data Extension",
                                 "icon":"document",
                                 "disable":False,
                                 "children":[
                                    {
                                       "id":"7",
                                       "name":"Data Enhancement Process",
                                       "icon":"document",
                                       "disable":False,
                                       "children":[
                                          {
                                             "id":"8",
                                             "name":"Business Analysis Report",
                                             "icon":"document",
                                             "disable":False
                                          },
                                          {
                                             "id":"9",
                                             "name":"Performance Overview",
                                             "icon":"document",
                                             "disable":False,
                                             "children":[
                                                {
                                                   "id":"10",
                                                   "name":"Manual Input for Performance",
                                                   "icon":"document",
                                                   "disable":False
                                                },
                                                {
                                                   "id":"11",
                                                   "name":"Post-Report Evaluation",
                                                   "icon":"document",
                                                   "disable": False
                                                }
                                             ]
                                          }
                                       ]
                                    }
                                 ]
                              }
                           ]
                        }
                     ]
                  }
               ]
            }
         ]
      }
   ]
}

checkItems = ["0","1","2","3","4","5","6","7","9","8"]
if "change" not in st.session_state:
    st.session_state["change"] = checkItems
if "i" not in st.session_state:
    st.session_state["i"] = 0
if "disable" not in st.session_state:
    st.session_state["disable"] = False 

change = st.button("Select index from 0 to 9")
if change:
    st.session_state["change"] = ["0", "1", "2", "3", "4", "5", "6", "7", "9", "8"]

change2 = st.button("Deselect all")
if change2:
    st.session_state["change"] = []

disable_toggle = st.button("Toggle Treeview View Enable/Disable")
if disable_toggle:
    st.session_state["disable"] = not st.session_state["disable"]

st.warning(f"Treeview disable! Current set: {st.session_state['disable']}")


result = tree_independent_components(treeItems, checkItems=st.session_state["change"],disable=st.session_state['disable'])

try:
  st.write(sorted(result["setSelected"], key=int))
except:
  pass

