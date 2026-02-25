"""
Notification Service component for the stock market analysis system.

Delivers daily reports through multiple communication channels:
- Telegram bot integration
- Slack webhook integration
- Email SMTP integration
"""

import logging
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Optional

import requests

from ..models import DailyReport, DeliveryResult
from .configuration_manager import ConfigurationManager


class NotificationService:
    """
    Delivers reports through multiple communication channels.
    
    Responsibilities:
    - Deliver reports via Telegram, Slack, and Email
    - Format reports appropriately for each channel
    - Handle channel-specific failures gracefully
    - Log all delivery attempts
    - Continue delivery through remaining channels on individual failures
    """
    
    def __init__(self, config_manager: ConfigurationManager):
        """
        Initialize the Notification Service.
        
        Args:
            config_manager: Configuration manager for accessing channel credentials
        """
        self.logger = logging.getLogger(__name__)
        self.config_manager = config_manager
    
    def deliver_report(self, report: DailyReport) -> DeliveryResult:
        """
        Delivers report through all configured channels.
        
        Args:
            report: The daily report to deliver
            
        Returns:
            DeliveryResult containing success/failure status for each channel
            
        Note:
            Continues delivery through remaining channels on individual failures.
            Each channel failure is isolated and logged independently.
        """
        self.logger.info(f"Starting delivery of report {report.report_id}")
        
        errors = {}
        
        # Attempt Telegram delivery - failures don't affect other channels
        telegram_success, telegram_error = self._attempt_telegram_delivery(report)
        if not telegram_success:
            errors['telegram'] = telegram_error or "Telegram delivery failed"
            self.logger.error(f"Telegram delivery failed for report {report.report_id}: {errors['telegram']}")
        
        # Attempt Slack delivery - failures don't affect other channels
        slack_success, slack_error = self._attempt_slack_delivery(report)
        if not slack_success:
            errors['slack'] = slack_error or "Slack delivery failed"
            self.logger.error(f"Slack delivery failed for report {report.report_id}: {errors['slack']}")
        
        # Attempt Email delivery - failures don't affect other channels
        email_success, email_error = self._attempt_email_delivery(report)
        if not email_success:
            errors['email'] = email_error or "Email delivery failed"
            self.logger.error(f"Email delivery failed for report {report.report_id}: {errors['email']}")
        
        result = DeliveryResult(
            telegram_success=telegram_success,
            slack_success=slack_success,
            email_success=email_success,
            errors=errors
        )
        
        # Log overall delivery result
        if result.all_succeeded():
            self.logger.info(f"Report {report.report_id} delivered successfully to all channels")
        elif result.any_succeeded():
            succeeded = [ch for ch in ['telegram', 'slack', 'email'] if ch not in errors]
            self.logger.warning(
                f"Report {report.report_id} partially delivered. "
                f"Succeeded: {succeeded}, Failed: {list(errors.keys())}"
            )
        else:
            self.logger.error(f"Report {report.report_id} failed to deliver to all channels")
        
        return result
    
    def _attempt_telegram_delivery(self, report: DailyReport) -> tuple[bool, Optional[str]]:
        """
        Attempts to deliver report via Telegram.
        
        Args:
            report: The daily report to deliver
            
        Returns:
            Tuple of (success status, error message if failed)
        """
        try:
            telegram_config = self.config_manager.get_telegram_config()
            
            if not telegram_config:
                return False, "No Telegram configuration found"
            
            # Format report for Telegram
            message = report.format_for_telegram()
            
            # Send to all configured chat IDs
            failed_chats = []
            for chat_id in telegram_config.chat_ids:
                try:
                    url = f"https://api.telegram.org/bot{telegram_config.bot_token}/sendMessage"
                    payload = {
                        'chat_id': chat_id,
                        'text': message,
                        'parse_mode': 'HTML'
                    }
                    
                    response = requests.post(url, json=payload, timeout=10)
                    
                    if response.status_code == 200:
                        self.logger.info(f"Telegram delivery successful to chat {chat_id}")
                    else:
                        error_msg = f"HTTP {response.status_code}: {response.text[:100]}"
                        self.logger.error(f"Telegram delivery failed to chat {chat_id}: {error_msg}")
                        failed_chats.append(f"{chat_id} ({error_msg})")
                
                except Exception as e:
                    self.logger.error(f"Telegram delivery exception for chat {chat_id}: {e}")
                    failed_chats.append(f"{chat_id} ({str(e)})")
            
            if failed_chats:
                return False, f"Failed to deliver to chats: {', '.join(failed_chats)}"
            
            return True, None
        
        except Exception as e:
            error_msg = f"Telegram delivery error: {str(e)}"
            self.logger.error(error_msg)
            return False, error_msg
    
    def _attempt_slack_delivery(self, report: DailyReport) -> tuple[bool, Optional[str]]:
        """
        Attempts to deliver report via Slack.
        
        Args:
            report: The daily report to deliver
            
        Returns:
            Tuple of (success status, error message if failed)
        """
        try:
            slack_config = self.config_manager.get_slack_config()
            
            if not slack_config:
                return False, "No Slack configuration found"
            
            # Format report for Slack
            message = report.format_for_slack()
            
            # Send to Slack webhook
            payload = {
                'channel': slack_config.channel,
                'text': message,
                'username': 'Stock Market Bot'
            }
            
            response = requests.post(slack_config.webhook_url, json=payload, timeout=10)
            
            if response.status_code == 200:
                self.logger.info(f"Slack delivery successful to channel {slack_config.channel}")
                return True, None
            else:
                error_msg = f"HTTP {response.status_code}: {response.text[:100]}"
                self.logger.error(f"Slack delivery failed: {error_msg}")
                return False, error_msg
        
        except Exception as e:
            error_msg = f"Slack delivery error: {str(e)}"
            self.logger.error(error_msg)
            return False, error_msg
    
    def _attempt_email_delivery(self, report: DailyReport) -> tuple[bool, Optional[str]]:
        """
        Attempts to deliver report via Email.
        
        Args:
            report: The daily report to deliver
            
        Returns:
            Tuple of (success status, error message if failed)
        """
        try:
            email_config = self.config_manager.get_email_config()
            
            if not email_config:
                return False, "No Email configuration found"
            
            # Format report for Email
            html_content = report.format_for_email()
            
            # Create email message
            msg = MIMEMultipart('alternative')
            msg['Subject'] = f"Daily Market Report - {report.trading_date}"
            msg['From'] = email_config.sender_address
            msg['To'] = ', '.join(email_config.recipients)
            
            # Attach HTML content
            html_part = MIMEText(html_content, 'html')
            msg.attach(html_part)
            
            # Send email via SMTP
            smtp_config = email_config.smtp
            
            if smtp_config.use_tls:
                server = smtplib.SMTP(smtp_config.host, smtp_config.port, timeout=10)
                server.starttls()
            else:
                server = smtplib.SMTP(smtp_config.host, smtp_config.port, timeout=10)
            
            try:
                server.login(smtp_config.username, smtp_config.password)
                server.sendmail(
                    email_config.sender_address,
                    email_config.recipients,
                    msg.as_string()
                )
                self.logger.info(f"Email delivery successful to {len(email_config.recipients)} recipients")
                return True, None
            finally:
                server.quit()
        
        except Exception as e:
            error_msg = f"Email delivery error: {str(e)}"
            self.logger.error(error_msg)
            return False, error_msg
    
    # Legacy methods for backward compatibility
    def deliver_to_telegram(self, report: DailyReport) -> bool:
        """Delivers report via Telegram. Returns success status."""
        success, _ = self._attempt_telegram_delivery(report)
        return success
    
    def deliver_to_slack(self, report: DailyReport) -> bool:
        """Delivers report via Slack. Returns success status."""
        success, _ = self._attempt_slack_delivery(report)
        return success
    
    def deliver_to_email(self, report: DailyReport) -> bool:
        """Delivers report via Email. Returns success status."""
        success, _ = self._attempt_email_delivery(report)
        return success
