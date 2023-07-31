from django.conf import settings
from django.core.mail import EmailMultiAlternatives

def send_user_mail(user):
    subject = 'Titulo del correo'
    html = """\
	
   
			<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">
			<html xmlns="http://www.w3.org/1999/xhtml">
			 
			<head>
			  <meta http-equiv="Content-Type" content="text/html; charset=utf-8" />
			  <title>Factura electronica</title>
			  <style type="text/css">
			  body {margin: 0; padding: 0; min-width: 100%!important;}
			  img {height: auto;}
			  .content {width: 100%; max-width: 600px;}
			  .header {padding: 40px 30px 20px 30px;}
			  .innerpadding {padding: 30px 30px 30px 30px;}
			  .borderbottom {border-bottom: 1px solid #f2eeed;}
			  .subhead {font-size: 15px; color: #ffffff; font-family: sans-serif; letter-spacing: 10px;}
			  .h1, .h2, .bodycopy {color: #153643; font-family: sans-serif;}
			  .h1 {font-size: 33px; line-height: 38px; font-weight: bold;}
			  .h2 {padding: 0 0 15px 0; font-size: 24px; line-height: 28px; font-weight: bold;}
			  .bodycopy {font-size: 16px; line-height: 22px;}
			  .button {text-align: center; font-size: 18px; font-family: sans-serif; font-weight: bold; padding: 0 30px 0 30px;}
			  .button a {color: #ffffff; text-decoration: none;}
			  .footer {padding: 20px 30px 15px 30px;}
			  .footercopy {font-family: sans-serif; font-size: 14px; color: #ffffff;}
			  .footercopy a {color: #ffffff; text-decoration: underline;}

			  @media only screen and (max-width: 550px), screen and (max-device-width: 550px) {
			  body[yahoo] .hide {display: none!important;}
			  body[yahoo] .buttonwrapper {background-color: transparent!important;}
			  body[yahoo] .button {padding: 0px!important;}
			  body[yahoo] .button a {background-color: #e05443; padding: 15px 15px 13px!important;}
			  body[yahoo] .unsubscribe {display: block; margin-top: 20px; padding: 10px 50px; background: #2f3942; border-radius: 5px; text-decoration: none!important; font-weight: bold;}
			  }

			  /*@media only screen and (min-device-width: 601px) {
			    .content {width: 600px !important;}
			    .col425 {width: 425px!important;}
			    .col380 {width: 380px!important;}
			    }*/

			  </style>
			</head>

			<body yahoo bgcolor="#f6f8f1">
			<table width="100%" bgcolor="#f6f8f1" border="0" cellpadding="0" cellspacing="0">
			<tr>
			  <td>
			    <!--[if (gte mso 9)|(IE)]>
			      <table width="600" align="center" cellpadding="0" cellspacing="0" border="0">
			        <tr>
			          <td>
			    <![endif]-->     
			    <table bgcolor="#ffffff" class="content" align="center" cellpadding="0" cellspacing="0" border="0">
			      <tr>
			        <td style=" background-image: linear-gradient(to left top, #0db9f8, #0790be, #0c6988, #0f4456, #0c222a);" class="header">
			          <table width="70" align="left" border="0" cellpadding="0" cellspacing="0">  
			            <tr>
			              <td height="70" style="padding: 0 20px 20px 0;">
			                <img class="fix" src="https://scontent.feoh1-1.fna.fbcdn.net/v/t39.30808-6/236831317_373363691048746_6124884787829342845_n.jpg?_nc_cat=109&ccb=1-5&_nc_sid=09cbfe&_nc_ohc=et8rIWzAmncAX_1J_Tz&_nc_ht=scontent.feoh1-1.fna&oh=00_AT8joP-X4KiB-powh_0SzwZndTG9a0wyD_gGCfdCc6tADQ&oe=6248B14E" width="70" height="70" border="0" alt="" />
			              </td>
			            </tr>
			          </table>
			          <!--[if (gte mso 9)|(IE)]>
			            <table width="425" align="left" cellpadding="0" cellspacing="0" border="0">
			              <tr>
			                <td>
			          <![endif]-->
			          <table class="col425" align="left" border="0" cellpadding="0" cellspacing="0" style="width: 100%; max-width: 425px;">  
			            <tr>
			              <td height="70">
			                <table width="100%" border="0" cellspacing="0" cellpadding="0">
			                  <tr>
			                    <td class="subhead" style="padding: 0 0 0 3px;">
			                      <span style="color: white;">Evansoft</span>
			                    </td>
			                  </tr>
			                  <tr>
			                    <td class="h1" style="padding: 5px 0 0 0;">
			                     <span style="color: white;">Restauración de contraseña</span>
			                    </td>
			                  </tr>
			                </table>
			              </td>
			            </tr>
			          </table>
			          <!--[if (gte mso 9)|(IE)]>
			                </td>
			              </tr>
			          </table>
			          <![endif]-->
			        </td>
			      </tr>
			      <tr>
			        <td class="innerpadding borderbottom">
			          <table width="100%" border="0" cellspacing="0" cellpadding="0">
			            <tr>
			              <td class="h2">
			               Hola,$(name)!
			              </td>
			            </tr>
			            <tr>
			              <td class="bodycopy">
			                Puedes restablecer tú contraseña dando click al boton de abajo.</a>
			              </td>
			            </tr>
			          </table>
			        </td>
			      </tr>
			      <tr>
			        <td class="innerpadding borderbottom">
			          <!--[if (gte mso 9)|(IE)]>
			            <table width="380" align="left" cellpadding="0" cellspacing="0" border="0">
			              <tr>
			                <td>
			          <![endif]-->
			          <table class="col380" align="left" border="0" cellpadding="0" cellspacing="0" style="width: 100%; max-width: 380px;">  
			            <tr>
			              <td>
			                <table width="100%" border="0" cellspacing="0" cellpadding="0">
			                  <tr>
			                    <td style="padding: 20px 0 0 0;">
			                      <table class="buttonwrapper" style="background-image: linear-gradient(to left bottom, #0db9f8, #0790be, #0c6988, #0f4456, #0c222a);" border="0" cellspacing="0" cellpadding="0">
			                        <tr>
			                          <td class="button" height="45">
			                            <a href="http://localhost:8000/NewPW/$(pk)/$(token)">Reestablecer</a>
			                          </td>			                        
			                        </tr>			                         
			                        </tr>
			                      </table>
			                    </td>
			                  </tr>
			                </table>
			              </td>
			            </tr>
			          </table>
			          <!--[if (gte mso 9)|(IE)]>
			                </td>
			              </tr>
			          </table>
			          <![endif]-->
			        </td>
			      </tr>
			      
			     
			    </table>
			    <!--[if (gte mso 9)|(IE)]>
			          </td>
			        </tr>
			    </table>
			    <![endif]-->
			    </td>
			  </tr>
			</table>

			</body>
			</html>

    """
    content = html.render({
        'user': 'hola',
    })

    message = EmailMultiAlternatives(subject, #Titulo
                                    '',
                                    settings.EMAIL_HOST_USER, #Remitente
                                    [user.email]) #Destinatario

    message.attach_alternative(content, 'text/html')
    message.send()