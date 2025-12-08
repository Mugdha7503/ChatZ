import streamlit as st
import requests

API_URL = "http://127.0.0.1:8000"

st.set_page_config(page_title="ChatZ", layout="wide")
st.title("📚 ChatZ – PDF AI Assistant")

# Initialize session keys
if "file_id" not in st.session_state:
    st.session_state.file_id = None
if "extracted" not in st.session_state:
    st.session_state.extracted = False
if "embeddings_done" not in st.session_state:
    st.session_state.embeddings_done = False

# ----------------------------
# ACCESS CONTROL
# ----------------------------

def restrict(page):
    """Show an error & stop page execution if access is invalid."""

    fid = st.session_state.file_id
    extracted = st.session_state.extracted
    embedded = st.session_state.embeddings_done

    # CONDITION 3 → No file
    if fid is None:
        if page != "Upload":
            st.error("❌ Please upload a PDF first.")
            st.stop()

    # CONDITION 2 → File uploaded but NO embeddings
    if fid and not embedded:
        if page not in ["Extract", "Embed"]:
            st.error("⚠️ Embeddings not ready. Please Extract → Embed first.")
            st.stop()

    # CONDITION 1 → File + embeddings ready
    if fid and embedded:
        if page != "Query":
            st.error("✔ Embeddings ready. Access allowed only to Query page.")
            st.stop()

# Sidebar Navigation
page = st.sidebar.radio("Navigation", ["Upload", "Extract", "Embed", "Query"])
restrict(page)



# ----------------------------
# PAGE: UPLOAD
# ----------------------------
if page == "Upload":
    st.header("📤 Upload PDF")

    uploaded = st.file_uploader("Select PDF file", type=["pdf"])

    if uploaded and st.button("Upload File"):
        files = {"file": uploaded}
        resp = requests.post(f"{API_URL}/upload/upload_file", files=files)

        if resp.status_code == 200:
            data = resp.json()

            st.session_state.file_id = data["file_id"]
            st.session_state.file_name = data["file_name"]
            st.session_state.embeddings_done = data["embedding_status"]
            st.session_state.extracted = False

            if st.session_state.embeddings_done:
                st.success("🎉 File exists and embeddings already available. Go to Query!")
            else:
                st.info("File uploaded. Please extract text.")

        else:
            st.error(resp.text)



# ----------------------------
# PAGE: EXTRACT
# ----------------------------
elif page == "Extract":
    st.header("📑 Extract Text")

    if st.button("Extract Text"):
        fid = st.session_state.file_id
        resp = requests.get(f"{API_URL}/extract/{fid}")

        if resp.status_code == 200:
            data = resp.json()
            st.success("Text extracted!")
            st.text_area("Preview", data["preview_text"])
            st.session_state.extracted = True
        else:
            st.error(resp.text)



# ----------------------------
# PAGE: EMBED
# ----------------------------
elif page == "Embed":
    st.header("🧠 Generate Embeddings")

    if not st.session_state.extracted:
        st.warning("Extract text first!")
    else:
        if st.button("Create Embeddings"):
            fid = st.session_state.file_id
            resp = requests.post(f"{API_URL}/embed/{fid}")

            if resp.status_code == 200:
                st.success("Embeddings created!")
                st.session_state.embeddings_done = True
            else:
                st.error(resp.text)



# ----------------------------
# PAGE: QUERY
# ----------------------------
elif page == "Query":
    st.header("💬 Ask Questions")

    q = st.text_input("Your question:")

    if st.button("Ask"):
        fid = st.session_state.file_id
        resp = requests.post(f"{API_URL}/query/", json={"question": q, "file_id": fid})

        if resp.status_code == 200:
            data = resp.json()
            st.success(data["answer"])

            st.subheader("Sources")
            for src in data["sources"]:
                st.write(src)

        else:
            st.error(resp.text)

# import streamlit as st
# import requests

# API_URL = "http://127.0.0.1:8000"

# st.set_page_config(page_title="ChatZ", layout="wide")

# st.title("📚 ChatZ – PDF AI Assistant")

# # ----------------------------
# # PAGE SELECTION
# # ----------------------------
# page = st.sidebar.radio("Navigation", ["Upload", "Extract", "Embed", "Query"])

# # ----------------------------
# # PAGE: UPLOAD
# # ----------------------------
# # ----------------------------
# # PAGE: UPLOAD
# # ----------------------------
# if page == "Upload":
#     st.header("📤 Upload PDF")

#     uploaded = st.file_uploader("Select PDF file", type=["pdf"])

#     if uploaded and st.button("Upload File"):
#         files = {"file": uploaded}
#         resp = requests.post(f"{API_URL}/upload/upload_file", files=files)

#         if resp.status_code == 200:
#             data = resp.json()

#             st.session_state.file_id = data["file_id"]
#             st.session_state.file_name = data["file_name"]
#             st.session_state.embedding_status = data["embedding_status"]

#             redirect_to = data.get("redirect_to", "extract")

#             if redirect_to == "query":
#                 st.success(
#                     f"📌 File '{st.session_state.file_name}' already exists and embeddings are ready.\n"
#                     "You can now go to the Query page to ask questions or access the chat bot."
#                 )
#                 st.session_state.page = "Query"
#                 st.session_state.embeddings_done = True

#             elif redirect_to == "extract":
#                 st.info(
#                     f"⚠️ File '{st.session_state.file_name}' exists but embeddings are not ready.\n"
#                     "Please go to the Extract page to extract text first."
#                 )
#                 st.session_state.page = "Extract"
#                 st.session_state.extracted = False

#             else:
#                 st.success("PDF uploaded successfully. You can now extract text.")
#                 st.session_state.page = "Extract"
#                 st.session_state.extracted = False

#             # Update URL query params (optional)
#             st.query_params = {"page": st.session_state.page}

#             st.stop()  # Stop to immediately rerun the script and reflect page change

#         else:
#             st.error(resp.text)

# # ----------------------------
# # PAGE: EXTRACT
# # ----------------------------
# elif page == "Extract":
#     st.header("📑 Extract Text")
    
#     if "extracted" not in st.session_state:
#         st.warning("Extract text first!")

#     elif "file_id" not in st.session_state:
#         st.warning("Upload a file first!")
#     else:
#         if st.button("Extract Text"):
#             fid = st.session_state.file_id
#             resp = requests.get(f"{API_URL}/extract/{fid}")

#             if resp.status_code == 200:
#                 data = resp.json()
#                 st.success("Text extracted!")
#                 st.text_area("Preview", data["preview_text"])
#                 st.session_state.extracted = True
#             else:
#                 st.error(resp.text)


# # ----------------------------
# # PAGE: EMBED
# # ----------------------------
# elif page == "Embed":
#     st.header("🧠 Generate Embeddings")

#     if "extracted" not in st.session_state:
#         st.warning("Extract text first!")
#     else:
#         if st.button("Create Embeddings"):
#             fid = st.session_state.file_id
#             resp = requests.post(f"{API_URL}/embed/{fid}")

#             if resp.status_code == 200:
#                 st.success("Embeddings created!")
#                 st.session_state.embeddings_done = True
#             else:
#                 st.error(resp.text)


# # ----------------------------
# # PAGE: QUERY
# # ----------------------------
# elif page == "Query":
#     st.header("💬 Ask Questions")

#     if "embeddings_done" not in st.session_state:
#         st.warning("Create embeddings first!")
#     else:
#         q = st.text_input("Your question:")

#         if st.button("Ask"):
#             fid = st.session_state.file_id
#             resp = requests.post(f"{API_URL}/query/", json={"question": q, "file_id": fid})

#             if resp.status_code == 200:
#                 data = resp.json()
#                 st.success(data["answer"])

#                 st.subheader("Sources")
#                 for src in data["sources"]:
#                     st.write(src)

#             else:
#                 st.error(resp.text)