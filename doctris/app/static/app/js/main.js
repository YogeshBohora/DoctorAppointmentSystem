
$(document)
.ready(function() {
    $('.ui.form.login-form')
    .form({
        fields: {
        username: {
            identifier  : 'username',
            rules: [
            {
                type   : 'empty',
                prompt : 'Please enter your username'
            },
            {
                type   : 'length[3]',
                prompt : 'Username must be 3 characters long'
            }
            ]
        },
        password: {
            identifier  : 'password',
            rules: [
            {
                type   : 'empty',
                prompt : 'Please enter your password'
            },
            {
                type   : 'length[6]',
                prompt : 'Password must be at least 6 characters'
            }
            ]
        }
        }
    })
    ;
})
;
$(document)
.ready(function() {
    $('.ui.form.admin-doc-form')
    .form({
        fields: {
        username: {
            identifier  : 'username',
            rules: [
            {
                type   : 'empty',
                prompt : 'Please enter username'
            },
            {
                type   : 'length[3]',
                prompt : 'Username must be 3 characters long'
            }
            ]
        },
        password: {
            identifier  : 'password',
            rules: [
            {
                type   : 'empty',
                prompt : 'Please enter password'
            },
            {
                type   : 'length[6]',
                prompt : 'Password must be at least 6 characters'
            }
            ]
        },
        first_name: {
            identifier  : 'first_name',
            rules: [
            {
                type   : 'empty',
                prompt : 'Please enter first name'
            },
            ]
        },
        last_name: {
            identifier  : 'last_name',
            rules: [
            {
                type   : 'empty',
                prompt : 'Please enter last name'
            },
            ]
        },
        email: {
            identifier  : 'email',
            rules: [
            {
                type   : 'empty',
                prompt : 'Please enter email'
            },
            {
                type   : 'email',
                prompt : 'Please valid email'
            }
            ]
        },
        phone: {
            identifier  : 'phone',
            rules: [
            {
                type   : 'empty',
                prompt : 'Please enter phone'
            },
            {
                type   : 'length[10]',
                prompt : 'Phone must be 10 characters long'
            }
            ]
        }
        }
    })
    ;
})
;

$(document)
.ready(function() {
    $('.ui.form.admin-pat-form')
    .form({
        fields: {
        username: {
            identifier  : 'username',
            rules: [
            {
                type   : 'empty',
                prompt : 'Please enter username'
            },
            {
                type   : 'length[3]',
                prompt : 'Username must be 3 characters long'
            }
            ]
        },
        password: {
            identifier  : 'password',
            rules: [
            {
                type   : 'empty',
                prompt : 'Please enter password'
            },
            {
                type   : 'length[6]',
                prompt : 'Password must be at least 6 characters'
            }
            ]
        },
        first_name: {
            identifier  : 'first_name',
            rules: [
            {
                type   : 'empty',
                prompt : 'Please enter first name'
            },
            ]
        },
        last_name: {
            identifier  : 'last_name',
            rules: [
            {
                type   : 'empty',
                prompt : 'Please enter last name'
            },
            ]
        },
        phone: {
            identifier  : 'phone',
            rules: [
            {
                type   : 'empty',
                prompt : 'Please enter phone'
            },
            {
                type   : 'length[10]',
                prompt : 'Phone must be 10 characters long'
            }
            ]
        }
        }
    })
    ;
})
;
