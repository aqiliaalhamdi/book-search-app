import streamlit as st
import pandas as pd
import json
import os
from datetime import datetime

# Konfigurasi halaman
st.set_page_config(
    page_title="Books to Scrape - Search Engine",
    page_icon="📚",
    layout="wide"
)

# Fungsi untuk memuat data
@st.cache_data
def load_data():
    """Memuat data buku dari file JSON"""
    try:
        with open('data/books.json', 'r', encoding='utf-8') as file:
            data = json.load(file)
        return pd.DataFrame(data)
    except FileNotFoundError:
        st.error("File books.json tidak ditemukan. Pastikan Anda telah menjalankan scraping terlebih dahulu.")
        return pd.DataFrame()
    except Exception as e:
        st.error(f"Error loading data: {str(e)}")
        return pd.DataFrame()

# Fungsi untuk menampilkan statistik
def show_statistics(df):
    """Menampilkan statistik data buku"""
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Buku", len(df))
    
    with col2:
        avg_rating = df['rating'].mean() if not df.empty else 0
        st.metric("Rating Rata-rata", f"{avg_rating:.1f}")
    
    with col3:
        if not df.empty and 'price' in df.columns:
            # Ekstrak harga numerik
            df['price_numeric'] = df['price'].str.extract(r'£(\d+\.\d+)').astype(float)
            avg_price = df['price_numeric'].mean()
            st.metric("Harga Rata-rata", f"£{avg_price:.2f}")
        else:
            st.metric("Harga Rata-rata", "N/A")
    
    with col4:
        available_books = df[df['availability'].str.contains('In stock', na=False)].shape[0] if not df.empty else 0
        st.metric("Buku Tersedia", available_books)

# Fungsi untuk filter data
def filter_data(df, search_term, min_rating, max_rating, availability_filter):
    """Filter data berdasarkan kriteria"""
    filtered_df = df.copy()
    
    if search_term:
        filtered_df = filtered_df[
            filtered_df['title'].str.contains(search_term, case=False, na=False)
        ]
    
    if min_rating > 0:
        filtered_df = filtered_df[filtered_df['rating'] >= min_rating]
    
    if max_rating < 5:
        filtered_df = filtered_df[filtered_df['rating'] <= max_rating]
    
    if availability_filter == "In Stock Only":
        filtered_df = filtered_df[filtered_df['availability'].str.contains('In stock', na=False)]
    
    return filtered_df

# Fungsi untuk menampilkan buku
def display_books(df):
    """Menampilkan daftar buku dalam format card"""
    for idx, book in df.iterrows():
        with st.container():
            col1, col2 = st.columns([1, 3])
            
            with col1:
                if book.get('image_url'):
                    st.image(book['image_url'], width=150)
                else:
                    st.info("No Image Available")
            
            with col2:
                st.subheader(book['title'])
                
                # Rating display
                rating_stars = "⭐" * int(book['rating']) + "☆" * (5 - int(book['rating']))
                st.write(f"Rating: {rating_stars} ({book['rating']}/5)")
                
                # Price dan availability
                col2a, col2b = st.columns(2)
                with col2a:
                    st.write(f"**Harga:** {book['price']}")
                with col2b:
                    st.write(f"**Ketersediaan:** {book['availability']}")
                
                # Description
                if book.get('description'):
                    st.write(f"**Deskripsi:** {book['description']}")
                
                # Link to original page
                if book.get('url'):
                    st.markdown(f"[Lihat di Website Original]({book['url']})")
                
                st.divider()

# Main application
def main():
    st.title("📚 Books to Scrape - Search Engine")
    st.markdown("---")
    
    # Load data
    df = load_data()
    
    if df.empty:
        st.warning("Tidak ada data untuk ditampilkan. Jalankan scraping terlebih dahulu.")
        return
    
    # Sidebar untuk filter
    with st.sidebar:
        st.header("Filter Pencarian")
        
        # Search box
        search_term = st.text_input("Cari Judul Buku", "")
        
        # Rating filter
        st.subheader("Rating")
        min_rating = st.slider("Rating Minimum", 0, 5, 0)
        max_rating = st.slider("Rating Maksimum", 0, 5, 5)
        
        # Availability filter
        availability_filter = st.selectbox(
            "Ketersediaan",
            ["All", "In Stock Only"]
        )
        
        # Sort options
        sort_by = st.selectbox(
            "Urutkan berdasarkan",
            ["Title", "Rating", "Price"]
        )
        
        sort_order = st.radio(
            "Urutan",
            ["Ascending", "Descending"]
        )
    
    # Apply filters
    filtered_df = filter_data(df, search_term, min_rating, max_rating, availability_filter)
    
    # Sort data
    if sort_by == "Title":
        filtered_df = filtered_df.sort_values('title', ascending=(sort_order == "Ascending"))
    elif sort_by == "Rating":
        filtered_df = filtered_df.sort_values('rating', ascending=(sort_order == "Ascending"))
    elif sort_by == "Price":
        if 'price' in filtered_df.columns:
            filtered_df['price_numeric'] = filtered_df['price'].str.extract(r'£(\d+\.\d+)').astype(float)
            filtered_df = filtered_df.sort_values('price_numeric', ascending=(sort_order == "Ascending"))
    
    # Show statistics
    st.subheader("Statistik Data")
    show_statistics(filtered_df)
    st.markdown("---")
    
    # Show results
    st.subheader(f"Hasil Pencarian ({len(filtered_df)} buku ditemukan)")
    
    if filtered_df.empty:
        st.info("Tidak ada buku yang sesuai dengan kriteria pencarian.")
    else:
        # Pagination
        books_per_page = 10
        total_pages = len(filtered_df) // books_per_page + (1 if len(filtered_df) % books_per_page > 0 else 0)
        
        if total_pages > 1:
            page_number = st.selectbox("Pilih Halaman", range(1, total_pages + 1))
            start_idx = (page_number - 1) * books_per_page
            end_idx = start_idx + books_per_page
            page_df = filtered_df.iloc[start_idx:end_idx]
        else:
            page_df = filtered_df
        
        display_books(page_df)

# Footer
def show_footer():
    st.markdown("---")
    st.markdown(
        """
        <div style='text-align: center; color: #666;'>
            <p>📚 Books to Scrape Search Engine | 
            Universitas Abulyatama | 
            Information Retrieval - 2025</p>
        </div>
        """,
        unsafe_allow_html=True
    )

if __name__ == "__main__":
    main()
    show_footer()