import datetime

# Local import
import const


def email_html_database(username):
    return '''
    <html lang="en">
    
        <head>
    
            <style>
                .awl a {
                    color: #FFFFFF;
                    text-decoration: none;
                }
    
                .abml a {
                    color: #000000;
                    font-family: Roboto-Medium, Helvetica, Arial, sans-serif;
                    font-weight: bold;
                    text-decoration: none;
                }
    
                .adgl a {
                    color: rgba(0, 0, 0, 0.87);
                    text-decoration: none;
                }
    
                .afal a {
                    color: #b0b0b0;
                    text-decoration: none;
                }
    
                @media screen and (min-width: 600px) {
                    .v2sp {
                        padding: 6px 30px 0px;
                    }
                    .v2rsp {
                        padding: 0px 10px;
                    }
                }
            </style>
        </head>
        <body bgcolor="#FFFFFF" style="margin: 0; padding: 0;">
            <table border="0" cellpadding="0" cellspacing="0" height="100%" style="min-width: 348px;" width="100%">
                <tbody>
                    <tr height="32px"></tr>
                    <tr align="center">
                        <td width="32px"></td>
                        <td>
                            <table border="0" cellpadding="0" cellspacing="0" style="max-width: 600px;">
                                <tbody>
                                    <tr height="16"></tr>
                                    <tr>
                                        <td>
                                            <table bgcolor="#00b5b8" border="0" cellpadding="0" cellspacing="0" style="min-width: 332px; max-width: 600px; border: 1px solid #F0F0F0; border-bottom: 0; border-top-left-radius: 3px; border-top-right-radius: 3px;" width="100%">
                                                <tbody>
                                                    <tr>
                                                        <td colspan="3" height="72px"></td>
                                                    </tr>
                                                    <tr>
                                                        <td width="32px"></td>
                                                        <td style="font-family: Roboto-Regular,Helvetica,Arial,sans-serif; font-size: 24px; color: #FFFFFF; line-height: 1.25; min-width: 300px; text-align: center;">Smarthepia database is not available</td>
                                                        <td width="32px"></td>
                                                    </tr>
                                                    <tr>
                                                        <td colspan="3" height="18px"></td>
                                                    </tr>
                                                </tbody>
                                            </table>
                                        </td>
                                    </tr>
                                    <tr>
                                        <td>
                                        <table bgcolor="#FFFFFF" border="0" cellpadding="0" cellspacing="0" style="min-width: 332px; max-width: 600px; border: 1px solid #F0F0F0; border-top: 0;" width="100%">
                                            <tbody>
                                                <tr>
                                                    <td colspan="3" height="18px"></td>
                                                </tr>
                                                <tr>
                                                    <td width="32px"></td>
                                                    <td style="font-family: Roboto-Regular,Helvetica,Arial,sans-serif; font-size: 13px; color: #202020; line-height: 1.5;">You received this message because your email is listed as the default or designate person to receive critical error from the Smarthepia network.</td>
                                                    <td width="10px"></td>
                                                </tr>
                                                <tr>
                                                    <td colspan="3" height="18px"></td>
                                                </tr>
                                            </tbody>
                                        </table>
                                        </td>
                                    </tr>
                                    <tr>
                                        <td>
                                            <table bgcolor="#FAFAFA" border="0" cellpadding="0" cellspacing="0" style="min-width: 332px; max-width: 600px; border: 1px solid #F0F0F0; border-bottom: 1px solid #C0C0C0; border-top: 0; border-bottom-left-radius: 3px; border-bottom-right-radius: 3px;" width="100%">
                                                <tbody>
                                                    <tr height="16px">
                                                        <td rowspan="3" width="32px"></td>
                                                        <td></td>
                                                        <td rowspan="3" width="32px"></td>
                                                    </tr>
                                                    <tr>
                                                        <td>
                                                            <table border="0" cellpadding="0" cellspacing="0" style="min-width: 300px;">
                                                                <tbody>
                                                                    <tr>
                                                                        <td style="font-family: Roboto-Regular,Helvetica,Arial,sans-serif; font-size: 13px; color: #202020; line-height: 1.5;padding-bottom: 4px;">Hi ''' + username + ''',</td>
                                                                    </tr>
                                                                    <tr>
                                                                        <td style="font-family: Roboto-Regular,Helvetica,Arial,sans-serif; font-size: 13px; color: #202020; line-height: 1.5;padding: 4px 0;">Today the ''' + datetime.datetime.now().strftime("%d.%m.%Y") + ''' at  ''' + datetime.datetime.now().strftime("%H:%M:%S") + ''' the connection to the Smarthepia database failed. As a result the whole system is not working properly.
                                                                            <br>
                                                                            <br><b>Don&#39;t recognize this activity?</b>
                                                                            <br>You may want to change <a  href="''' + const.ws_profile + '''" style="text-decoration: none; color: #4285F4;" target="_blank">to change</a> your password now.
                                                                        </td>
                                                                    </tr>
                                                                    <tr>
                                                                        <td style="font-family: Roboto-Regular,Helvetica,Arial,sans-serif; font-size: 13px; color: #202020; line-height: 1.5; padding-top: 28px;">Smarthepia account team</td>
                                                                    </tr>
                                                                    <tr height="16px"></tr>
                                                                    <tr>
                                                                        <td>
                                                                            <table style="font-family: Roboto-Regular,Helvetica,Arial,sans-serif; font-size: 12px; co=lor: #B9B9B9; line-height: 1.5;">
                                                                                <tbody>
                                                                                    <tr>
                                                                                        <td>This html can't receive replies. For more information, visit the <a href="''' + const.ws_help + '''" style="text-decoration: none; color: #4285F4;" target="_blank">Smartehepia Accounts Help Center</a>.</td>
                                                                                    </tr>
                                                                                </tbody>
                                                                            </table>
                                                                        </td>
                                                                    </tr>
                                                                </tbody>
                                                            </table>
                                                        </td>
                                                    </tr>
                                                    <tr height="32px"></tr>
                                                </tbody>
                                            </table>
                                        </td>
                                    </tr>
                                    <tr height="16"></tr>
                                    <tr>
                                        <td style="max-width: 600px; font-family: Roboto-Regular,Helvetica,Arial,sans-serif; font-size: 10px; color: #BCBCBC; line-height: 1.5;"></td>
                                    </tr>
                                    <tr>
                                        <td>
                                            <table style="font-family: Roboto-Regular,Helvetica,Arial,sans-serif; font-size: 10px; color: #666666; line-height: 18px; padding-bottom: 10px">
                                                <tbody>
                                                    <tr height="6px"></tr>
                                                    <tr>
                                                        <td>
                                                            <div style="direction: ltr; text-align: left">&copy; hepia, Rue de la Prairie 4, 1202 Geneva Switzerland</div>
                                                            <div style="display: none !important; mso-hide:all; max-height:0px; max-width:0px;">1528665583736000</div>
                                                        </td>
                                                    </tr>
                                                </tbody>
                                            </table>
                                        </td>
                                    </tr>
                                </tbody>
                            </table>
                        </td>
                        <td width="32px"></td>
                    </tr>
                    <tr height="32px"></tr>
                </tbody>
            </table>
        </body>
    </html>
    '''
