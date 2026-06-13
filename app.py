import pickle
import streamlit as st
import pandas as pd

# Load saved model files
books      = pickle.load(open('book_list.pkl', 'rb'))
similarity = pickle.load(open('similarity.pkl', 'rb'))

# Page config 
st.set_page_config(
    page_title="Book Recommender",
    page_icon="📚",
    layout="wide"
)

# Custom CSS
st.markdown("""
<style>
    /* Main background and font */
    .stApp {
        background-color: #0f1117;
        color: #e8e8e8;
    }

    /* Title styling */
    .main-title {
        font-size: 2.8rem;
        font-weight: 800;
        background: linear-gradient(135deg, #a78bfa, #60a5fa);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 0.2rem;
    }

    .subtitle {
        color: #9ca3af;
        font-size: 1rem;
        margin-bottom: 2rem;
    }

    /* Book card */
    .book-card {
        background: #1e2130;
        border: 1px solid #2d3148;
        border-radius: 12px;
        padding: 1.2rem 1rem;
        margin-bottom: 0.5rem;
        transition: border-color 0.2s;
    }
    .book-card:hover {
        border-color: #a78bfa;
    }
    .book-rank {
        font-size: 1.6rem;
        font-weight: 900;
        color: #a78bfa;
        line-height: 1;
    }
    .book-title {
        font-size: 0.95rem;
        font-weight: 700;
        color: #f3f4f6;
        margin: 0.4rem 0 0.2rem;
        line-height: 1.3;
    }
    .book-author {
        font-size: 0.8rem;
        color: #9ca3af;
    }
    .book-meta {
        display: flex;
        gap: 0.6rem;
        margin-top: 0.6rem;
        flex-wrap: wrap;
    }
    .badge {
        font-size: 0.72rem;
        padding: 2px 8px;
        border-radius: 99px;
        font-weight: 600;
    }
    .badge-rating {
        background: #1a2e1a;
        color: #4ade80;
        border: 1px solid #166534;
    }
    .badge-sim {
        background: #1e1a2e;
        color: #a78bfa;
        border: 1px solid #5b21b6;
    }
    .badge-lang {
        background: #1a2535;
        color: #60a5fa;
        border: 1px solid #1e40af;
    }

    /* Selected book info box */
    .selected-box {
        background: linear-gradient(135deg, #1e1a2e, #1a2535);
        border: 1px solid #3730a3;
        border-radius: 12px;
        padding: 1.4rem 1.6rem;
        margin-bottom: 1.5rem;
    }
    .selected-label {
        font-size: 0.75rem;
        text-transform: uppercase;
        letter-spacing: 0.1em;
        color: #a78bfa;
        font-weight: 700;
        margin-bottom: 0.4rem;
    }
    .selected-title {
        font-size: 1.4rem;
        font-weight: 800;
        color: #f9fafb;
        margin-bottom: 0.3rem;
    }
    .selected-author {
        color: #9ca3af;
        font-size: 0.9rem;
    }

    /* Sidebar top books */
    .top-book-item {
        display: flex;
        align-items: flex-start;
        gap: 0.6rem;
        padding: 0.6rem 0;
        border-bottom: 1px solid #2d3148;
    }
    .top-book-num {
        font-size: 0.75rem;
        font-weight: 700;
        color: #a78bfa;
        min-width: 1.2rem;
        padding-top: 2px;
    }
    .top-book-title {
        font-size: 0.8rem;
        color: #e5e7eb;
        line-height: 1.3;
    }
    .top-book-rating {
        font-size: 0.75rem;
        color: #4ade80;
        margin-top: 2px;
    }

    /* Section header */
    .section-header {
        font-size: 1.1rem;
        font-weight: 700;
        color: #f3f4f6;
        margin: 1.5rem 0 1rem;
        padding-bottom: 0.5rem;
        border-bottom: 1px solid #2d3148;
    }

    /* Hide streamlit default footer */
    footer { visibility: hidden; }
    #MainMenu { visibility: hidden; }
</style>
""", unsafe_allow_html=True)


# Recommendation function 
def recommend(book_title):
    """Returns list of 5 recommended books and the matched title."""
    matches = books[books['title'].str.lower() == book_title.lower()]

    if matches.empty:
        partial = books[books['title'].str.lower().str.contains(
            book_title.lower(), na=False, regex=False
        )]
        if partial.empty:
            return None, None
        book_title = partial.iloc[0]['title']

    index = books[books['title'].str.lower() == book_title.lower()].index[0]
    distances = sorted(
        list(enumerate(similarity[index])),
        reverse=True,
        key=lambda x: x[1]
    )[1:6]

    results = []
    for i, score in distances:
        row = books.iloc[i]
        results.append({
            'title':    row['title'],
            'author':   row['authors'],
            'rating':   row.get('average_rating', 'N/A'),
            'language': row.get('language_code', 'N/A'),
            'score':    round(float(score), 3)
        })
    return results, book_title


def get_book_info(title):
    """Return metadata for the selected book."""
    match = books[books['title'].str.lower() == title.lower()]
    if match.empty:
        return None
    row = match.iloc[0]
    return {
        'title':    row['title'],
        'author':   row['authors'],
        'rating':   row.get('average_rating', 'N/A'),
        'language': row.get('language_code', 'N/A'),
    }

# Main content
st.markdown('<div class="main-title">📚 Book Recommender</div>', unsafe_allow_html=True)
st.markdown(
    '<div class="subtitle">Discover your next favourite read using content-based filtering</div>',
    unsafe_allow_html=True
)

# Search input
col_search, col_select = st.columns([1, 2])

with col_search:
    search_query = st.text_input(
        "🔍 Search by keyword",
        placeholder="e.g. Harry, Tolkien, magic…"
    )

# Filter book list by search query
all_titles = sorted(books['title'].tolist())
if search_query.strip():
    filtered_titles = [
        t for t in all_titles
        if search_query.lower() in t.lower()
    ]
    if not filtered_titles:
        filtered_titles = all_titles
        st.warning(f"No titles match '{search_query}'. Showing all books.")
else:
    filtered_titles = all_titles

with col_select:
    selected_book = st.selectbox(
        "📖 Select a book",
        filtered_titles,
        index=0
    )

# Show selected book info
if selected_book:
    info = get_book_info(selected_book)
    if info:
        st.markdown(
            f"""<div class="selected-box">
                <div class="selected-label">Selected Book</div>
                <div class="selected-title">{info['title']}</div>
                <div class="selected-author">✍️ {info['author']}</div>
                <div class="book-meta" style="margin-top:0.8rem">
                    <span class="badge badge-rating">⭐ {info['rating']}</span>
                    <span class="badge badge-lang">🌐 {info['language']}</span>
                </div>
            </div>""",
            unsafe_allow_html=True
        )

# Recommend button
if st.button("Get Recommendations →", type="primary", use_container_width=False):
    with st.spinner("Finding similar books…"):
        results, matched_title = recommend(selected_book)

    if results is None:
        st.error("Book not found. Please try a different title or keyword.")
    else:
        if matched_title and matched_title.lower() != selected_book.lower():
            st.info(f"Showing results for closest match: **{matched_title}**")

        st.markdown(
            f'<div class="section-header">Books similar to "{matched_title}"</div>',
            unsafe_allow_html=True
        )

        cols = st.columns(5)
        for idx, (col, book) in enumerate(zip(cols, results)):
            with col:
                sim_pct = int(book['score'] * 100)
                st.markdown(
                    f"""<div class="book-card">
                        <div class="book-rank">#{idx + 1}</div>
                        <div class="book-title">{book['title']}</div>
                        <div class="book-author">✍️ {book['author']}</div>
                        <div class="book-meta">
                            <span class="badge badge-rating">⭐ {book['rating']}</span>
                            <span class="badge badge-sim">~{sim_pct}% match</span>
                            <span class="badge badge-lang">🌐 {book['language']}</span>
                        </div>
                    </div>""",
                    unsafe_allow_html=True
                )

st.markdown("---")
st.caption("Built with Python · Scikit-learn · Streamlit &nbsp;|&nbsp; Dataset: Goodreads Books (Kaggle)")
