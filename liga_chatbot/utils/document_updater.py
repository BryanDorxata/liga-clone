import os
import io
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload
import pypandoc
import requests
from pathlib import Path

class DocumentUpdater:
    def __init__(self, credentials_path=None):
        """
        Initialize DocumentUpdater with Google Drive API credentials
        
        Args:
            credentials_path: Path to service account JSON file
        """
        self.credentials_path = credentials_path
        self.service = None
        self.folder_id = "1JmMuoMr6CswsphQVD10DG5UsTpBHYp6m"
        
    def authenticate(self):
        """Authenticate with Google Drive API"""
        if self.credentials_path and os.path.exists(self.credentials_path):
            credentials = Credentials.from_service_account_file(
                self.credentials_path,
                scopes=['https://www.googleapis.com/auth/drive.readonly']
            )
            self.service = build('drive', 'v3', credentials=credentials)
        else:
            raise ValueError("Credentials file not found. Please provide valid service account credentials.")
    
    def get_folder_files(self):
        """Get all files from the specified Google Drive folder"""
        if not self.service:
            self.authenticate()
            
        try:
            query = f"'{self.folder_id}' in parents and trashed=false"
            results = self.service.files().list(
                q=query,
                fields="files(id, name, mimeType, size)"
            ).execute()
            
            return results.get('files', [])
        except Exception as e:
            print(f"Error getting folder files: {e}")
            return []
    
    def download_file(self, file_id, file_name):
        """Download file from Google Drive"""
        try:
            request = self.service.files().get_media(fileId=file_id)
            file_io = io.BytesIO()
            downloader = MediaIoBaseDownload(file_io, request)
            
            done = False
            while done is False:
                status, done = downloader.next_chunk()
                
            file_io.seek(0)
            return file_io.getvalue()
        except Exception as e:
            print(f"Error downloading {file_name}: {e}")
            return None
    
    def convert_to_markdown(self, file_content, file_name, mime_type):
        """Convert file content to markdown format"""
        try:
            # Save temporary file
            temp_file = f"/tmp/{file_name}"
            with open(temp_file, 'wb') as f:
                f.write(file_content)
            
            # Convert based on mime type
            if mime_type == 'application/pdf':
                # For PDF files, use pypandoc
                markdown_content = pypandoc.convert_file(temp_file, 'md', format='pdf')
            elif mime_type in ['application/vnd.google-apps.document', 'application/msword', 
                              'application/vnd.openxmlformats-officedocument.wordprocessingml.document']:
                # For Word documents
                markdown_content = pypandoc.convert_file(temp_file, 'md')
            elif mime_type in ['text/plain', 'text/csv']:
                # For text files
                with open(temp_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                markdown_content = f"```\n{content}\n```"
            else:
                # Default: treat as text
                with open(temp_file, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()
                markdown_content = f"```\n{content}\n```"
            
            # Clean up temp file
            os.remove(temp_file)
            
            return markdown_content
        except Exception as e:
            print(f"Error converting {file_name} to markdown: {e}")
            return f"# {file_name}\n\n*Error converting file to markdown*\n\n"
    
    def update_documentation(self, docs_path="liga_documentation.md"):
        """Main function to update documentation with Google Drive files"""
        try:
            # Get all files from folder
            files = self.get_folder_files()
            
            if not files:
                print("No files found in the folder")
                return
            
            # Start building markdown content
            markdown_content = "# Liga ng mga Barangay sa Pilipinas Documentation\n\n"
            markdown_content += f"*Last updated: {os.popen('date').read().strip()}*\n\n"
            markdown_content += "---\n\n"
            
            # Process each file
            for file_info in files:
                file_id = file_info['id']
                file_name = file_info['name']
                mime_type = file_info['mimeType']
                
                print(f"Processing: {file_name}")
                
                # Download file
                file_content = self.download_file(file_id, file_name)
                
                if file_content:
                    # Convert to markdown
                    file_markdown = self.convert_to_markdown(file_content, file_name, mime_type)
                    
                    # Add to documentation
                    markdown_content += f"## {file_name}\n\n"
                    markdown_content += file_markdown
                    markdown_content += "\n\n---\n\n"
                else:
                    markdown_content += f"## {file_name}\n\n"
                    markdown_content += "*Error downloading file*\n\n---\n\n"
            
            # Write to documentation file
            docs_file_path = Path(__file__).parent / docs_path
            with open(docs_file_path, 'w', encoding='utf-8') as f:
                f.write(markdown_content)
            
            print(f"Documentation updated successfully: {docs_file_path}")
            
        except Exception as e:
            print(f"Error updating documentation: {e}")

def update_liga_docs(credentials_path=None):
    """Convenience function to update Liga documentation"""
    updater = DocumentUpdater(credentials_path)
    updater.update_documentation()

if __name__ == "__main__":
    # Example usage
    update_liga_docs()
