import streamlit as st


def llm_page():
    
    st.title("🤖 Prediction")
    
    st.write("This page is under construction222.")
    
    mistral_key = st.text_input("Enter your Mistral key:")

    if mistral_key != "MISTRAL":
        st.error("Mistral key is not valid.")
    else:
        st.success("Mistral key is valid.")