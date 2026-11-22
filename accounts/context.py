def layout(request):
    mobile = request.session.get('mobile', False)
    return {
        'is_mobile': mobile,
        'admin_shell': 'admin_portal/shell_mobile.html' if mobile else 'admin_portal/shell_desktop.html',
    }