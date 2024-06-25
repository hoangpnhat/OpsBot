from app.common.config import cfg, logger
from app.database.base import BaseCollection
from app.database.schemas import LastMessage, SurveySchema
from datetime import datetime, timedelta
import os
import sys
import requests


class Survey:
    def __init__(self):
        self.collection_survey = BaseCollection("survey")
        self.collection_last_message = BaseCollection("last_message")

    def save_last_message(self, thread_id: str, message_id: str, sender_id: str, bot_id: str) -> None:
        """
        This function saves the last message id of a thread

        Args:
            thread_id (str): The thread id if it is direct message, or subthread_id if it is a subthread
            message_id (str): The message id
        """
        try:
            if len(self.collection_last_message.find({"thread_id": thread_id})) > 0:
                query = {
                    "thread_id": thread_id,
                    "survey_sent": False,
                }
                update = {
                    "$set": {
                        "message_id": message_id,
                        "message_sent_at": datetime.now(),
                    }
                }
                self.collection_last_message.update(query, update)
            else:
                data = LastMessage(
                    thread_id=thread_id,
                    message_id=message_id,
                    sender_id=sender_id,
                    bot_id=bot_id,
                    message_sent_at=datetime.now(),
                    survey_sent=False,
                    survey_sent_at=None,
                    survey_id=None
                ).model_dump()
                self.collection_last_message.insert_one(data)
        except Exception as e:
            exc_type, _, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            msg = f"Error: {e}" + f"err_type: {exc_type}, err_file: {fname}, err_line: {exc_tb.tb_lineno}"
            
            logger.error(f"Cannot save the last message id! {msg} \
                          \n thread_id: {thread_id}, message_id: {message_id}")
            

    def get_available_threads(self) -> list:
        """
        This function retrieves all available threads which has message_sent_at + 30 min < now

        Returns:
            list: The list of available threads
        """
        try:
            time_30_minutes_ago = datetime.now() - timedelta(minutes=cfg.min_minutes_to_sent_survey)

            # Query to find records where message_sent_at < now - 30 mins
            query = {
                "message_sent_at": {
                    "$lt": time_30_minutes_ago
                },
                "survey_sent": False
            }

            available_threads = self.collection_last_message.find(query)
            return available_threads
        except Exception as e:
            exc_type, _, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            msg = f"Error: {e}" + f"err_type: {exc_type}, err_file: {fname}, err_line: {exc_tb.tb_lineno}"
            
            logger.error(f"Cannot get the available threads! {msg}")
            return []
        
    def insert_survey(self, thread_id: str, message_id: str, question: str) -> str:
        """
        Insert a survey record to the database

        Args:
            thread_id (str): The thread id
            message_id (str): The message id
            question (str): The question
        
        Returns:
            str: The inserted id
        """
        survey = SurveySchema(
            thread_id=thread_id,
            message_id=message_id,
            send_at=datetime.now(),
            is_completed=False,
            completed_at=None,
            question=question,
            feedback=None,
            feedback_id=None
        ).model_dump()
        survey_id = self.collection_survey.insert_one(survey)
        return survey_id

    def update_after_sending(self, thread_id: str, message_id: str, survey_id: str) -> None:
        """
        This function updates the last message record after sending the survey

        Args:
            thread_id (str): The thread id
            message_id (str): The message id
            survey_id (str): The survey id
        
        Returns:
            None
        """
        try:
            query = {
                "thread_id": thread_id,
                "message_id": message_id,
            }
            update = {
                "$set": {
                    "survey_sent": True,
                    "survey_sent_at": datetime.now(),
                    "survey_id": survey_id,
                }
            }
            self.collection_last_message.update(query, update)
        except Exception as e:
            exc_type, _, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            msg = f"Error: {e}" + f"err_type: {exc_type}, err_file: {fname}, err_line: {exc_tb.tb_lineno}"
            
            logger.error(f"Cannot update the last message record after sending the survey! {msg} \
                          \n thread_id: {thread_id}, message_id: {message_id}")

    def send_survey(self):
        """
        This function sends the survey to the available threads
        """
        try:
            url = os.environ.get("GAPO_BOT_API_URL")
            headers = {
                "x-gapo-api-key": os.environ.get("GAPO_BOT_KEY"),
                "Content-Type": "application/json"
            }

            available_threads = self.get_available_threads()
            for thread in available_threads:
                thread_id = thread.get("thread_id")
                bot_id = thread.get("bot_id")
                message_id = thread.get("message_id")
                data = {
                    "thread_id": int(thread_id),
                    "bot_id": int(bot_id),
                    "body": {
                        "type": "carousel",
                        "metadata": {
                            "carousel_cards": [
                                {
                                    "title": cfg.survey_question,
                                    "image_url": "https://gapo-work-image.s3.vn-hcm.zetaby.com/images/478adb11-3d05-4cd9-bf56-b2826c4474cc/blob.jpeg",
                                    "buttons": [{"title": ans, "type": "postback", "payload": id}
                                        for ans, id in zip(cfg.answer_options, cfg.answer_option_ids)]
                                }
                            ]
                        }
                    }
                }
                response = requests.post(url, headers=headers, json=data)
                if response.status_code == 200:
                    logger.debug(f"Survey sent successfully. Thread id (sub): {thread_id}, message id: {message_id}")
                    survey_id = self.insert_survey(thread_id, message_id, cfg.survey_question)
                    self.update_after_sending(thread_id, message_id, survey_id)
                else:
                    raise requests.RequestException(f"Failed to send the survey! \
                                                    Status code: {response.status_code}, Message: {response.json()}")

        except Exception as e:
            exc_type, _, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            msg = f"Error: {e}" + f"err_type: {exc_type}, err_file: {fname}, err_line: {exc_tb.tb_lineno}"
            
            logger.error(f"Cannot send the survey! {msg}")

    def update_feedback(self, thread_id: str, feedback: str, feedback_id: str) -> None:
        """
        This function updates the feedback after receiving the feedback
        """

        query = {
            "thread_id": thread_id,
            "is_completed": False
        }

        update = {
            "$set": {
                "feedback": feedback,
                "is_completed": True,
                "completed_at": datetime.now(),
                "feedback_id": feedback_id
            }
        }

        updated_id = self.collection_survey.update(query, update)
        return updated_id
        
