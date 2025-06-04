import streamlit as st
import jwt
import logging
from datetime import datetime
import os
from typing import Dict, Any, Tuple, List
import re

from amazon_bulk_generator.auth.wordpress_auth import WordPressAuth
from amazon_bulk_generator.core.generator import BulkSheetGenerator, CampaignSettings
from amazon_bulk_generator.core.validators import (
    validate_keywords,
    validate_skus,
    validate_campaign_settings,
    validate_name_template
)
from amazon_bulk_generator.utils.file_handlers import FileHandler
from amazon_bulk_generator.utils.formatters import TextFormatter, DataFormatter

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class BulkCampaignApp:
    def __init__(self):
        self.generator = BulkSheetGenerator()
        self.file_handler = FileHandler()
        self.text_formatter = TextFormatter()
        self.data_formatter = DataFormatter()
        self.auth = WordPressAuth()
        
        self.part_mapping = {
            "SKU": "[SKU]",
            "AD TYPE": "SP",
            "MATCH TYPE": "match_type",
            "START DATE": "250423",
            "ROOT GROUP": "[Root]",
            "KEYWORD": "[KW]",
            "AG": "AG"
        }

    def run(self):
        """Run the Streamlit application"""
        # Check authentication first
        query_params = st.query_params
        token = query_params.get("token")
        
        if token:
            # If token is present in URL, try to validate it
            try:
                # Validate JWT token
                payload = jwt.decode(token, self.auth.secret_key, algorithms=["HS256"])
                st.session_state.wp_token = token
                st.session_state.user_id = payload.get("user_id")
            except jwt.ExpiredSignatureError:
                st.error("❌ Session expired. Please login again.")
                self.auth.show_login_page()
                return
            except jwt.InvalidTokenError:
                st.error("❌ Invalid token. Access denied.")
                self.auth.show_login_page()
                return
        
        # Check if user is authenticated
        if not self.auth.check_auth():
            self.auth.show_login_page()
            return

        # Create columns for header with logo
        col1, col2, col3 = st.columns([3, 1, 1])
        with col1:
            st.title("Amazon Ads Bulk Campaign Generator 🎯")
            st.markdown("Create properly formatted bulk sheets for Amazon Sponsored Products campaigns")
        with col2:
            st.image("ECommercean-Logo (1).png", width=200)
        with col3:
            if st.button("Logout"):
                st.session_state.clear()
                self.auth.logout()
                st.experimental_set_query_params()
                st.rerun()

        # Initialize session state
        if 'step' not in st.session_state:
            st.session_state.step = 1
            st.session_state.keywords = []
            st.session_state.skus = []
            st.session_state.keyword_group_size = None
            st.session_state.sku_group_size = None

        # Step 1: Keywords + SKUs Input
        if st.session_state.step == 1:
            st.header("Step 1: Enter Keywords and SKUs")

            col1, col2 = st.columns(2)
            with col1:
                keywords, keywords_error, keyword_group_size = self.get_keywords_input()
            with col2:
                skus, skus_error, sku_group_size = self.get_skus_input()

            # Navigation section
            st.markdown("<br>", unsafe_allow_html=True)
            nav_container = st.container()
            with nav_container:
                if keywords and skus and not keywords_error and not skus_error:
                    st.success(f"✅ Loaded {len(keywords)} keywords and {len(skus)} SKUs")

                    col1, col2, col3 = st.columns([1, 2, 1])
                    with col2:
                        if st.button("Continue to Campaign Settings ➡️", type="primary", use_container_width=True):
                            st.session_state.keywords = keywords
                            st.session_state.skus = skus
                            st.session_state.keyword_group_size = keyword_group_size
                            st.session_state.sku_group_size = sku_group_size
                            st.session_state.step = 2
                            st.rerun()

        # Step 2: Campaign Settings
        elif st.session_state.step == 2:
            st.header("Step 2: Configure Campaign Settings")
            settings, settings_error = self.get_campaign_settings()

            with st.container():
                st.markdown("---")
                col1, col2, col3 = st.columns([1, 2, 1])
                with col1:
                    if st.button("⬅️ Back to Step 1", use_container_width=True):
                        st.session_state.step = 1
                        st.rerun()
                with col2:
                    if settings and not settings_error:
                        if st.button("🎯 Generate Bulk Sheet", type="primary", use_container_width=True):
                            if 'keywords' not in st.session_state or 'skus' not in st.session_state:
                                st.error("Keywords/SKUs missing. Go back to Step 1.")
                                return

                            campaign_settings = CampaignSettings(
                                daily_budget=settings.daily_budget,
                                start_date=settings.start_date,
                                match_types=settings.match_types,
                                bids=settings.bids,
                                campaign_name_template=settings.campaign_name_template,
                                ad_group_name_template=settings.ad_group_name_template,
                                keyword_group_size=settings.keyword_group_size,
                                sku_group_size=settings.sku_group_size
                            )

                            self.generate_bulk_sheet(
                                st.session_state.keywords,
                                st.session_state.skus,
                                campaign_settings
                            )

    def get_keywords_input(self) -> Tuple[list, bool, int]:
        """Get and validate keywords input"""
        input_method = st.radio(
            "Choose input method for keywords:",
            ["Type/Paste", "Upload CSV"],
            help="Select how you want to input your keywords"
        )
        
        keywords = []
        has_error = False
        group_size = None
        
        if input_method == "Type/Paste":
            sample_data = self.file_handler.load_template_data('keywords')
            use_sample = st.checkbox("Load sample keywords")
            
            keyword_text = st.text_area(
                "Enter keywords",
                value=sample_data if use_sample else "",
                height=150,
                help="Enter keywords (one per line or comma-separated)"
            )
            
            if keyword_text:
                keywords = self.text_formatter.clean_text_input(keyword_text)
        else:
            keyword_file = st.file_uploader(
                "Upload keywords CSV",
                type=['csv']
            )
            if keyword_file:
                try:
                    keywords = self.file_handler.load_csv_data(keyword_file)
                except Exception as e:
                    st.error(f"Error loading keywords: {str(e)}")
                    has_error = True
        
        if keywords and not has_error:
            valid, error = validate_keywords(keywords)
            if not valid:
                st.error(error)
                has_error = True
            else:
                st.success(f"Successfully loaded {len(keywords)} keywords")
                
                enable_grouping = st.checkbox(
                    "Enable keyword grouping",
                    help="Group multiple keywords into a single campaign"
                )
                
                if enable_grouping:
                    group_size = st.number_input(
                        "Keywords per group",
                        min_value=1,
                        max_value=len(keywords),
                        value=min(3, len(keywords))
                    )
                    
                    if group_size:
                        st.write("Preview of keyword groups:")
                        groups = [keywords[i:i + group_size] for i in range(0, len(keywords), group_size)]
                        for i, group in enumerate(groups, 1):
                            with st.expander(f"Group {i}", expanded=(i == 1)):
                                st.write("\n".join(group))
        
        return keywords, has_error, group_size

    def get_skus_input(self) -> Tuple[list, bool, int]:
        """Get and validate SKUs input"""
        input_method = st.radio(
            "Choose input method for SKUs:",
            ["Type/Paste", "Upload CSV"],
            help="Select how you want to input your SKUs"
        )
        
        skus = []
        has_error = False
        group_size = None
        
        if input_method == "Type/Paste":
            sample_data = self.file_handler.load_template_data('skus')
            use_sample = st.checkbox("Load sample SKUs")
            
            sku_text = st.text_area(
                "Enter SKUs",
                value=sample_data if use_sample else "",
                height=150,
                help="Enter SKUs (one per line or comma-separated)"
            )
            
            if sku_text:
                skus = self.text_formatter.clean_text_input(sku_text)
        else:
            sku_file = st.file_uploader(
                "Upload SKUs CSV",
                type=['csv']
            )
            if sku_file:
                try:
                    skus = self.file_handler.load_csv_data(sku_file)
                except Exception as e:
                    st.error(f"Error loading SKUs: {str(e)}")
                    has_error = True
        
        if skus and not has_error:
            valid, error = validate_skus(skus)
            if not valid:
                st.error(error)
                has_error = True
            else:
                st.success(f"Successfully loaded {len(skus)} SKUs")
                
                enable_grouping = st.checkbox(
                    "Enable SKU grouping",
                    help="Group multiple SKUs into a single campaign"
                )
                
                if enable_grouping:
                    group_size = st.number_input(
                        "SKUs per group",
                        min_value=1,
                        max_value=len(skus),
                        value=min(3, len(skus))
                    )
                    
                    if group_size:
                        st.write("Preview of SKU groups:")
                        groups = [skus[i:i + group_size] for i in range(0, len(skus), group_size)]
                        for i, group in enumerate(groups, 1):
                            with st.expander(f"Group {i}", expanded=(i == 1)):
                                st.write("\n".join(group))
        
        return skus, has_error, group_size

    def _arrange_template_parts(self, title: str, available_parts: List[str], default_parts: List[str]) -> str:
        """Create a user-friendly interface for arranging template parts"""
        st.markdown(f"### 📝 {title}")
        
        key = f"{title}_selected_parts"
        if key not in st.session_state:
            st.session_state[key] = default_parts.copy()
        
        # Custom text input
        col1, col2 = st.columns([3, 1])
        with col1:
            custom_text = st.text_input(
                "Add custom text",
                key=f"{title}_custom",
                help="Letters, numbers, spaces, hyphens and underscores allowed"
            )
        with col2:
            if custom_text:
                if not re.match(r'^[a-zA-Z0-9\s_-]+$', custom_text.strip()):
                    st.error("Only letters, numbers, spaces, hyphens, and underscores allowed")
                elif st.button("Add", key=f"{title}_add_custom"):
                    clean_text = custom_text.strip()
                    if clean_text and clean_text not in st.session_state[key]:
                        st.session_state[key].append(clean_text)
                        st.rerun()

        tab1, tab2 = st.tabs(["Arrange Parts", "Add Parts"])
        
        with tab1:
            st.markdown("##### Current Parts:")
            selected_parts = st.session_state[key]
            
            for i, part in enumerate(selected_parts):
                col1, col2, col3 = st.columns([0.1, 0.8, 0.1])
                with col1:
                    if i > 0:
                        if st.button("↑", key=f"{title}_up_{i}"):
                            selected_parts[i], selected_parts[i-1] = selected_parts[i-1], selected_parts[i]
                            st.rerun()
                with col2:
                    st.info(part)
                with col3:
                    if i < len(selected_parts) - 1:
                        if st.button("↓", key=f"{title}_down_{i}"):
                            selected_parts[i], selected_parts[i+1] = selected_parts[i+1], selected_parts[i]
                            st.rerun()
            
            if selected_parts:
                st.markdown("##### Remove parts:")
                cols = st.columns(4)
                for idx, part in enumerate(selected_parts):
                    col_idx = idx % 4
                    with cols[col_idx]:
                        if st.button(f"❌ {part}", key=f"{title}_remove_{part}"):
                            st.session_state[key].remove(part)
                            st.rerun()
        
        with tab2:
            st.markdown("##### Available parts:")
            available = [p for p in available_parts if p not in st.session_state[key]]
            if available:
                cols = st.columns(3)
                for idx, part in enumerate(available):
                    col_idx = idx % 3
                    with cols[col_idx]:
                        if st.button(f"➕ {part}", key=f"{title}_add_{part}"):
                            st.session_state[key].append(part)
                            st.rerun()
            else:
                st.info("All parts have been added")

        template_values = [self.part_mapping.get(part, part) for part in selected_parts]
        template = "_".join(template_values)
        
        st.markdown("##### Template Preview")
        st.code(template)
        
        if template:
            st.markdown("##### Example Output")
            example = template.replace("[SKU]", "ABC123").replace("match_type", "exact").replace("[KW]", "keyword")
            st.code(example)
        
        return template

    def get_campaign_settings(self) -> Tuple[CampaignSettings, bool]:
        """Get and validate campaign settings"""
        has_error = False
        
        col1, col2 = st.columns(2)
        
        with col1:
            available_parts = ["SKU", "AD TYPE", "MATCH TYPE", "START DATE", "ROOT GROUP", "KEYWORD"]
            default_parts = ["SKU", "AD TYPE", "MATCH TYPE"]
            
            campaign_name_template = self._arrange_template_parts(
                "Campaign Name Template",
                available_parts,
                default_parts
            )
            
            ag_available_parts = ["AG", "SKU", "MATCH TYPE", "START DATE", "ROOT GROUP", "KEYWORD"]
            ag_default_parts = ["AG", "MATCH TYPE", "SKU"]
            
            ad_group_name_template = self._arrange_template_parts(
                "Ad Group Name Template",
                ag_available_parts,
                ag_default_parts
            )
            
            daily_budget = st.number_input(
                "Daily Budget ($)",
                min_value=1.0,
                value=10.0,
                help="Minimum daily budget is $1.00"
            )
            
            start_date = st.date_input(
                "Campaign Start Date",
                min_value=datetime.today(),
                help="Choose when your campaign should start"
            )
        
        with col2:
            match_types = st.multiselect(
                "Select Match Types",
                ["exact", "phrase", "broad"],
                default=["exact"]
            )
            
            bids = {}
            for match_type in match_types:
                bids[match_type] = st.number_input(
                    f"Default bid for {match_type} match ($)",
                    min_value=0.02,
                    value=0.75
                )
        
        settings = CampaignSettings(
            daily_budget=daily_budget,
            start_date=start_date,
            match_types=match_types,
            bids=bids,
            campaign_name_template=campaign_name_template,
            ad_group_name_template=ad_group_name_template,
            keyword_group_size=st.session_state.get('keyword_group_size'),
            sku_group_size=st.session_state.get('sku_group_size')
        )
        
        valid, error = validate_campaign_settings(settings)
        if not valid:
            st.error(error)
            has_error = True
        
        return settings, has_error

    def generate_bulk_sheet(self, keywords: list, skus: list, settings: CampaignSettings):
        """Generate and display bulk sheet"""
        try:
            df = self.generator.generate_bulk_sheet(keywords, skus, settings)
            preview_df = self.data_formatter.prepare_preview_data(df)
            
            excel_path = self.file_handler.save_bulk_sheet(df, 'xlsx')
            csv_path = self.file_handler.save_bulk_sheet(df, 'csv')
            
            st.success("Bulk sheet generated successfully!")
            
            col1, col2 = st.columns(2)
            with col1:
                with open(excel_path, 'rb') as f:
                    st.download_button(
                        "Download Excel File",
                        f.read(),
                        file_name=os.path.basename(excel_path),
                        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                    )
            
            with col2:
                with open(csv_path, 'rb') as f:
                    st.download_button(
                        "Download CSV File",
                        f.read(),
                        file_name=os.path.basename(csv_path),
                        mime="text/csv"
                    )
            
            st.markdown("### 🔍 Preview")
            st.dataframe(preview_df)
            
        except Exception as e:
            logger.error(f"Error generating bulk sheet: {str(e)}")
            st.error(f"Error generating bulk sheet: {str(e)}")
