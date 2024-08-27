from jira.model.issue_base import IssueBase
from datetime import datetime

import pytz

tz = pytz.timezone('America/Lima')


class Feature(IssueBase):
    def __init__(self):
        super().__init__()
        # self.project_jira_name = ''
        self.team_backlog_id = ''
        self.pi_result = ''
        # self.team_backlog_name = ''
        self.label_ttv_name = ''
        self.label_one_name = ''
        self.label_portfolio_id = ''
        self.label_sda_tool_id = ''
        #
        self.sprint_estimate = ''
        self.acceptance_criteria = ''
        self.business_value = ''
        self.project_sda_name = ''
        self.project_sda_tool_id = ''
        self.deliverable_id = ''
        self.type_of_delivery_name = ''
        self.time_in_status_blocked = ''

    def convert_json_to_feature(self, json_jira):

        # variables de JiraBase
        fields = json_jira.get('fields')
        changelog = json_jira.get('changelog')
        histories = changelog.get('histories')

        self._add_attr_basic(json_jira)
        self._get_attr_from_histories(histories)
        # variables solo de Feature

        labels = fields["labels"]
        for label in labels:
            label_without_sharp = label.replace("#", "")
            if label_without_sharp[0:3] == 'DE_':
                self.label_one_name = label_without_sharp
            if label_without_sharp[0:3] == 'TTV':
                self.label_ttv_name = label_without_sharp[4:len(label)]
            if label_without_sharp[0:7] == 'SDATOOL':
                self.label_sda_tool_id = label_without_sharp

        self.labels = ', '.join(fields.get('labels'))
        self.pi_result = ', '.join(fields.get('customfield_10264'))
        if fields.get('customfield_10272') is not None:
            self.sprint_estimate = fields.get('customfield_10272').get('value')
        self.acceptance_criteria = fields.get('customfield_10260')
        self.business_value = fields.get('customfield_10003')

        issuelinks = fields.get('issuelinks')
        for issue in issuelinks:
            if issue.get('outwardIssue') is not None:
                if issue.get('outwardIssue').get('fields') is not None:
                    sda = issue.get('outwardIssue').get('fields').get('summary')
                    self.project_sda_name = sda[0:-7].strip()
                    self.project_sda_tool_id = 'SDATOOL-' + sda[-6:-1]

        if fields.get('customfield_12900') is not None:
            self.deliverable_id = ', '.join(fields.get('customfield_12900'))
        if fields.get('customfield_19001') is not None:
            self.type_of_delivery_name = fields.get('customfield_19001').get('value')
        self.time_in_status_blocked = fields.get('customfield_10400')

        return self
