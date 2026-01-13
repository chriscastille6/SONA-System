"""
OSF Client for fetching repository files

Connects to Open Science Framework to retrieve study materials.
"""

import aiohttp
import asyncio
from typing import Dict, List, Any
from pathlib import Path


class OSFClient:
    """Client for interacting with OSF API."""
    
    OSF_API_BASE = "https://api.osf.io/v2"
    
    def __init__(self):
        self.session = None
    
    async def fetch_repo_files(self, osf_url: str) -> Dict[str, Any]:
        """
        Fetch files from OSF repository.
        
        Args:
            osf_url: OSF project URL (e.g., https://osf.io/abc123/)
        
        Returns:
            Dict containing file listings and download links
        """
        project_id = self._extract_project_id(osf_url)
        
        if not project_id:
            return {
                'error': 'Could not extract project ID from OSF URL',
                'url': osf_url
            }
        
        try:
            async with aiohttp.ClientSession() as session:
                self.session = session
                
                # Get project info
                project_info = await self._get_project_info(project_id)
                
                # Get file listing
                files = await self._get_file_listing(project_id)
                
                # Get file download links
                file_data = {
                    'project_id': project_id,
                    'project_title': project_info.get('data', {}).get('attributes', {}).get('title', 'Unknown'),
                    'files': files,
                    'file_count': len(files),
                    'note': 'File contents can be downloaded via provided links for detailed analysis'
                }
                
                return file_data
                
        except Exception as e:
            return {
                'error': f'OSF fetch failed: {str(e)}',
                'project_id': project_id
            }
    
    def _extract_project_id(self, osf_url: str) -> str:
        """
        Extract project ID from OSF URL.
        
        Args:
            osf_url: Full OSF URL
        
        Returns:
            Project ID string or empty string if not found
        """
        # Handle various OSF URL formats:
        # https://osf.io/abc123/
        # https://osf.io/abc123
        # abc123
        
        if 'osf.io/' in osf_url:
            parts = osf_url.split('osf.io/')
            if len(parts) > 1:
                project_id = parts[1].strip('/').split('/')[0]
                return project_id
        
        # Assume it's just the ID
        return osf_url.strip('/')
    
    async def _get_project_info(self, project_id: str) -> Dict:
        """Get project metadata from OSF API."""
        url = f"{self.OSF_API_BASE}/nodes/{project_id}/"
        
        async with self.session.get(url) as response:
            if response.status == 200:
                return await response.json()
            else:
                return {'error': f'HTTP {response.status}'}
    
    async def _get_file_listing(self, project_id: str) -> List[Dict]:
        """Get list of files in the project."""
        url = f"{self.OSF_API_BASE}/nodes/{project_id}/files/osfstorage/"
        
        files = []
        
        async with self.session.get(url) as response:
            if response.status == 200:
                data = await response.json()
                
                for item in data.get('data', []):
                    attrs = item.get('attributes', {})
                    file_info = {
                        'name': attrs.get('name', 'Unknown'),
                        'kind': attrs.get('kind', 'file'),
                        'size': attrs.get('size', 0),
                        'download_link': item.get('links', {}).get('download', ''),
                        'path': attrs.get('materialized_path', ''),
                    }
                    files.append(file_info)
        
        return files
    
    async def download_file_content(self, download_url: str) -> str:
        """
        Download and extract text from a file.
        
        Args:
            download_url: Direct download URL for the file
        
        Returns:
            Text content of the file
        """
        try:
            async with self.session.get(download_url) as response:
                if response.status == 200:
                    content = await response.read()
                    # Try to decode as text
                    try:
                        return content.decode('utf-8')
                    except UnicodeDecodeError:
                        return f"[Binary file - {len(content)} bytes]"
                else:
                    return f"[Download failed: HTTP {response.status}]"
        except Exception as e:
            return f"[Download error: {e}]"







