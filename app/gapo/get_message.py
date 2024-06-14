import requests
import os
import sys
from typing import List, Dict
from app.common.config import cfg, logger
from app.gapo.gapo_token import tokenizer


class MessageGetter:
    def __init__(self):
        self.url = os.environ.get("GAPO_BASE_API_URL") + 'messages'
        try:
            access_token = tokenizer.get_access_token()
        except Exception as e:
            logger.error(f"Failed to get access token from Gapo! {e}. \
                         We will try to use the environment variable GAPO_ACCESS_TOKEN instead")
            access_token = os.environ.get("GAPO_ACCESS_TOKEN")
        self.headers = {
            "Accept": "application/json",
            "X-Gapo-Workspace-Id": str(os.environ.get("GAPO_WORKSPACE_ID")),
            "Content-Type": "application/json",
            "Authorization": f"Bearer {access_token}"
        }
    def get_messages(self, thread_id: int, page_size: int = cfg.n_subthread_mesages) -> List[Dict] | List:
        """
        Get messages from a subthread or direct message

        Args: 
            thread_id (int): The thread id
            page_size (int): The number of messages to retrieve
        
        Returns:
            List[Dict]: A list of messages
        """
        params = {
            "thread_id": thread_id,
            "page_size": page_size
        }
        try:
            response = requests.get(self.url, headers=self.headers, params=params)
            if response.status_code == 200:
                logger.debug("Messages retrieved successfully")
                return response.json()['data']
            else:
                logger.error(f"Failed to retrieve messages from Gapo! \
                            Status code {response.status_code}, Response {response.json()}")
                return []
        except Exception as e:
            logger.error(f"Failed to retrieve messages from Gapo! {e}")
            return []
        
