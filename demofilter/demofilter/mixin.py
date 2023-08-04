class OnlyMeMixin:
    def process_queryset_for_permission(self, queryset, user, code):
        if user.is_authenticated and code:
            try:
                perm=user.user_roll.LSProlepermissions_roll.get(
                    lsp_permissions__permissions_code=code)
            except:
                perm=None
            if perm and perm.permission_level == 'only_me':
                if hasattr(queryset.model, 'owner'):
                    queryset = queryset.filter(owner = user)
                elif hasattr(queryset.model, 'user'):
                    queryset = queryset.filter(user = user)
        return queryset
        
    def get_queryset(self):
        qs = super().get_queryset()
        user = self.request.user
        print(self.PERMISSION_CODE)
        return self.process_queryset_for_permission(qs, user, self.PERMISSION_CODE)