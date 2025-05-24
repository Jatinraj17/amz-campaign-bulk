# WordPress Integration Guide for Amazon Bulk Campaign Generator

## Files to Share
1. Source Code (ZIP these folders/files):
   - `src/amazon_bulk_generator/` (entire directory)
   - `requirements.txt`
   - `streamlit_app.py`

## Server Requirements
1. Python Environment:
   - Python 3.7 or higher
   - pip (Python package manager)
   - Virtual environment capability

2. System Requirements:
   - Ability to run Python applications
   - Minimum 1GB RAM
   - 500MB disk space

## Installation Steps for WordPress Developer

1. Server Setup:
```bash
# Create a directory for the application
mkdir amazon-bulk-tool
cd amazon-bulk-tool

# Create and activate virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install requirements
pip install -r requirements.txt
```

2. WordPress Integration Options:

   A. Subdomain Setup (Recommended):
   - Create a subdomain (e.g., tools.ecommercean.com)
   - Configure the subdomain to point to the Streamlit application
   - Run the Streamlit app as a service:
   ```bash
   streamlit run streamlit_app.py --server.port 8501
   ```
   - Set up a reverse proxy (Nginx/Apache) to forward requests

   B. iFrame Integration:
   - Add this code to your WordPress page:
   ```html
   <iframe 
     src="http://your-domain:8501"
     width="100%" 
     height="800px" 
     frameborder="0"
   ></iframe>
   ```

3. Process Management:
   - Use systemd or supervisor to manage the Streamlit process
   - Example systemd service file:
   ```ini
   [Unit]
   Description=Amazon Bulk Campaign Generator
   After=network.target

   [Service]
   User=www-data
   WorkingDirectory=/path/to/amazon-bulk-tool
   ExecStart=/path/to/amazon-bulk-tool/venv/bin/streamlit run streamlit_app.py
   Restart=always

   [Install]
   WantedBy=multi-user.target
   ```

## Security Considerations
1. Set up SSL/TLS certificates
2. Configure proper firewall rules
3. Implement rate limiting
4. Keep Python packages updated

## Maintenance
1. Regular backups of the application
2. Monitor application logs
3. Set up error notifications
4. Keep system packages updated

## Support
For technical questions or issues:
1. Check the application logs
2. Review the Streamlit documentation
3. Contact the application developer

## Testing
After installation:
1. Test the application through the WordPress interface
2. Verify all features work as expected
3. Check mobile responsiveness
4. Test file upload/download functionality
