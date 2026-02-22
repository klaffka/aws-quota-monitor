import boto3
import os
import logging

logger = logging.getLogger(__name__)

class QuotaAlert:
    """Alert system for quota utilization thresholds"""
    
    def __init__(self, session=None, sns_topic_arn=None, threshold_pct=80):
        """
        Initialize QuotaAlert
        
        Args:
            session: boto3 session
            sns_topic_arn: ARN of SNS topic for alerts
            threshold_pct: Utilization percentage threshold (default 80%)
        """
        if session is None:
            session = boto3.Session()
        
        self.session = session
        self.sns_client = session.client('sns')
        self.sns_topic_arn = sns_topic_arn or os.environ.get('QM_ALERT_TOPIC_ARN')
        self.threshold_pct = threshold_pct
    
    def check_and_alert(self, quota):
        """
        Check quota utilization against threshold and send alert if exceeded
        
        Args:
            quota: Quota entry dict with keys like 'quotaName', 'utilizationPct', etc.
            
        Returns:
            bool: True if alert was sent, False otherwise
        """
        if not self.sns_topic_arn:
            logger.warning("SNS topic ARN not configured, skipping alert")
            return False
        
        utilization = quota.get('utilizationPct', 0)
        
        if utilization >= self.threshold_pct:
            self._send_alert(quota, utilization)
            return True
        
        return False
    
    def _send_alert(self, quota, utilization):
        """Send SNS alert for quota threshold breach"""
        try:
            message = self._format_alert_message(quota, utilization)
            subject = f"⚠️ Quota Alert: {quota.get('quotaName', 'Unknown')} - {utilization:.1f}%"
            
            response = self.sns_client.publish(
                TopicArn=self.sns_topic_arn,
                Subject=subject,
                Message=message
            )
            
            logger.info(f"Alert sent for {quota.get('quotaCode')} - MessageId: {response['MessageId']}")
        except Exception as e:
            logger.error(f"Failed to send alert: {e}")
    
    def _format_alert_message(self, quota, utilization):
        """Format alert message with quota details"""
        return f"""
Quota Utilization Alert
{'=' * 50}

Quota Name:      {quota.get('quotaName', 'Unknown')}
Quota Code:      {quota.get('quotaCode', 'Unknown')}
Service:         {quota.get('serviceCode', 'Unknown')}
Account ID:      {quota.get('accountId', 'Unknown')}
Region:          {quota.get('region', 'Unknown')}

Utilization:     {utilization:.1f}%
Threshold:       {self.threshold_pct}%

Current Usage:   {quota.get('usageValue', 0):.0f}
Limit:           {quota.get('limitValue', 0):.0f}

Scope Type:      {quota.get('scopeType', 'Unknown')}
Collector Type:  {quota.get('collectorType', 'Unknown')}
Data Source:     {quota.get('dataSource', 'Unknown')}

Collected At:    {quota.get('collectedAt', 'Unknown')}

{'-' * 50}
Please review your quota usage and take appropriate action if necessary.
""".strip()
