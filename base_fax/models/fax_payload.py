# -*- coding: utf-8 -*-
##############################################################################
#
#    Author: Dave Lasley <dave@laslabs.com>
#    Copyright: 2015 LasLabs, Inc.
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
from openerp import models, fields, api, tools
from PIL import Image
from io import BytesIO


class FaxPayload(models.Model):
    _name = 'fax.payload'
    _description = 'Fax Data Object'
    _phone_name_sequence = 10
    _country_fields = 'country_id'
    #  _partner_field = None
    
    ref = fields.Char(
        string='Fax Reference ID',
    )
    image = fields.Binary(
        string='Fax Image',
        attachment=True,
        readonly=True,
        required=True,
    )
    image_type = fields.Selection(
        [
            ('PDF', 'PDF'),
            ('PNG', 'PNG'),
            ('JPG', 'JPG'),
            ('BMP', 'BMP'),
            ('GIF', 'GIF'),
        ],
        default='PDF',
        required=True,
    )
    receipt_transmission_id = fields.One2many(
        'fax.payload.transmission',
    )
    transmission_ids = fields.Many2one(
        'fax.payload.transmission',
    )

    def __convert_image(self, base64_encoded_image, image_type, ):
        ''' Convert image for storage and use by the fax adapter '''
        binary = base64_encoded_image.decode('base64')
        with BytesIO(binary) as raw_image:
            image = Image.open(raw_image)
            with BytesIO() as new_raw:
                image.save(new_raw, image_type)
                return new_raw.getvalue().encode('base64')

    def send(self, fax_number, ):
        '''
        Sends fax. Designed to be overridden in submodules
        :param  fax_number:    str Number to fax to
        :return fax.payload.transmission:   Representing fax transmission
        '''
        return False   #  < fax.payload.transmission record

    @api.model
    def create(self, vals, ):
        if vals.get('image'):
            vals['image'] = self.__convert_image(
                vals['image'], vals['image_type']
            )
        super(FaxPayload, self).create(vals)

    @api.one
    def write(self, vals, ):
        if vals.get('image'):
            image_type = vals.get('image_type') or self.image_type
            vals['image'] = self.__convert_image(
                vals['image'], vals['image_type']
            )
        elif vals.get('image_type'):
            vals['image'] = self.__convert_image(
                self.image, vals['image_type']
            )
        super(FaxPayload, self).write(vals)
