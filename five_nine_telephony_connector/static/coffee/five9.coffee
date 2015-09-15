##############################################################################
#
#    Five9.js Library
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

class Five9
    
    WSDL = 'http://localhost:8080/agent/v2?wsdl'
    
    constructor: (@phoneNumber, @wsdl=WSDL) ->
        
    errorHandler: (msg) ->
        console.error(msg)
        
    makeCall: (callNumber, campaignId=false, checkDnc=false) ->
        data = {
            'number': callNumber,
            'campaignId': campaignId,
            'checkDnc': checkDnc,
            'callbackId': @phoneNumber
        }
        console.debug(data)
        $.soap({
            
            url: @WSDL,
            method: 'makeCall',
            
            data: data,
            
            success: (res) ->
                console.log(res)
            ,
            
            error: (res) ->
                errorHandler(res)
            ,
            
        })
