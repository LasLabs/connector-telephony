# -*- encoding: utf-8 -*-
##############################################################################
#
#    Five9 connector module for Odoo
#    Written by Dave Lasley <dave@laslabs.com>
#    Copyright (C) 2015 LasLabs, Inc. [https://laslabs.com]
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################
from openerp import models, fields, api, _
from openerp.exceptions import Warning
import logging
import base64
from suds.client import Client


_logger = logging.getLogger(__name__)


class ResUsers(models.Model):
    _inherit = "res.users"

    five9_billing_number = fields.Char(string='Five9 Billing Number')
    five9_calling_number = fields.Char(
        string="Five9 Calling Number", help="The phone number that will "
        "be presented during a click2dial")
    five9_login = fields.Char()
    five9_password = fields.Char()
    five9_email = fields.Char()
    is_admin = fields.Boolean()


class PhoneCommon(models.Model):
    ''' Five9 Phone connector module '''
    _inherit = 'phone.common'
    SERVER_WSDL = 'https://api.five9.com/wsadmin/v2/AdminWebService?wsdl&user=%s'
    CTI_WSDL = 'http://localhost:8080/agent/v2?wsdl'
    
    @api.one
    def _compute_cti_client(self, ):
        ''' Create an authed SOAP client to CTI Web Services
            using current logged in user
        '''
        headers = {
            #'Accept-Encoding':'gzip, deflate',
            'Content-Type':'text/xml;charset=UTF-8',
        }
        self.five9_cti_client = Client(self.CTI_WSDL, headers=headers)
    
    @api.one
    def _compute_web_client(self, ):
        ''' Create an authed SOAP client to Remote Web Services
            using current logged in user
        '''

        authorization = base64.b64encode('%s:%s' % (
            self.env._uid.five9_login, self.env._uid.five9_password
        ))
        headers = {
            #'Accept-Encoding':'gzip, deflate',
            'Content-Type':'text/xml;charset=UTF-8',
            'Authorization':'Basic %s' % authorization,
        }
        
        self.five9_web_client = Client(self.SERVER_WSDL % self.env._uid.five9_email,
                                       headers=headers)

    five9_cti_client = fields.Binary(compute='_compute_cti_client',
                                     readonly=True, store=False)
    five9_web_client = fields.Binary(compute='_compute_web_client',
                                     readonly=True, store=False)

    @api.model
    def click2dial(self, erp_number):
        ''' Generate a call using logged in user '''
        res = super(PhoneCommon, self).click2dial(erp_number)

        user = self.env._uid
        
        if not user.five9_calling_number:
            raise Warning(
                _('Missing Five9 Calling Number on user %s') % user.name)

        calling_number = self.convert_to_dial_number(erp_number)
        _logger.debug(
            'Starting Five9 makeCall request with '
            'calling number = %s and called_number = %s'
            % (user.five9_calling_number, calling_number))

        try:
            self.client.service.makeCall()
            
            soap.telephonyClick2CallDo(
                user.five9_login,
                user.five9_password,
                user.five9_calling_number,
                calling_number,
                user.five9_billing_number)
            _logger.info("Five9 telephonyClick2CallDo successfull")

        except Exception, e:
            _logger.error(
                "Error in the Five9 telephonyClick2CallDo request")
            _logger.error(
                "Here are the details of the error: '%s'" % unicode(e))
            raise Warning(
                _("Click to call to Five9 failed.\nHere is the error: "
                    "'%s'")
                % unicode(e))

        res['dialed_number'] = calling_number
        return res
