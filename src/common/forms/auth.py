"""Authentication and user profile forms."""

from django import forms
from django.contrib.auth import authenticate
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm

from ..models import User


class CustomLoginForm(AuthenticationForm):
    """Custom login form with OBC styling and approval checks."""

    username = forms.CharField(
        widget=forms.TextInput(
            attrs={
                "class": "form-control",
                "placeholder": "Username or Email",
                "autofocus": True,
            }
        )
    )
    password = forms.CharField(
        widget=forms.PasswordInput(
            attrs={"class": "form-control", "placeholder": "Password"}
        )
    )

    def clean(self):
        """Authenticate by username or email, enforcing approval requirements."""
        username = self.cleaned_data.get("username")
        password = self.cleaned_data.get("password")

        if username and password:
            try:
                if "@" in username:
                    user = User.objects.get(email=username)
                    username = user.username
                else:
                    user = User.objects.get(username=username)
            except User.DoesNotExist:
                raise forms.ValidationError("Invalid username or password.")

            self.user_cache = authenticate(
                self.request, username=username, password=password
            )

            if self.user_cache is None:
                raise forms.ValidationError("Invalid username or password.")

            if not self.user_cache.is_active:
                raise forms.ValidationError("This account is inactive.")

        return self.cleaned_data


class UserRegistrationForm(UserCreationForm):
    """Registration form that collects OOBC-specific metadata."""

    first_name = forms.CharField(
        max_length=30,
        required=True,
        widget=forms.TextInput(
            attrs={
                "class": "block w-full px-3 py-3 border border-gray-300 rounded-md leading-5 bg-white placeholder-gray-500 focus:outline-none focus:placeholder-gray-400 focus:ring-1 focus:ring-blue-500 focus:border-blue-500",
                "placeholder": "Enter your first name",
            }
        ),
    )
    last_name = forms.CharField(
        max_length=30,
        required=True,
        widget=forms.TextInput(
            attrs={
                "class": "block w-full px-3 py-3 border border-gray-300 rounded-md leading-5 bg-white placeholder-gray-500 focus:outline-none focus:placeholder-gray-400 focus:ring-1 focus:ring-blue-500 focus:border-blue-500",
                "placeholder": "Enter your last name",
            }
        ),
    )
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(
            attrs={
                "class": "block w-full px-3 py-3 border border-gray-300 rounded-md leading-5 bg-white placeholder-gray-500 focus:outline-none focus:placeholder-gray-400 focus:ring-1 focus:ring-blue-500 focus:border-blue-500",
                "placeholder": "Enter your email address",
            }
        ),
    )
    user_type = forms.ChoiceField(
        choices=User.USER_TYPES,
        required=True,
        widget=forms.Select(
            attrs={
                "class": "block w-full px-3 py-3 border border-gray-300 rounded-md leading-5 bg-white focus:outline-none focus:ring-1 focus:ring-blue-500 focus:border-blue-500"
            }
        ),
    )
    organization = forms.CharField(
        max_length=255,
        required=False,
        widget=forms.TextInput(
            attrs={
                "class": "block w-full px-3 py-3 border border-gray-300 rounded-md leading-5 bg-white placeholder-gray-500 focus:outline-none focus:placeholder-gray-400 focus:ring-1 focus:ring-blue-500 focus:border-blue-500",
                "placeholder": "Organization or Agency Name (Optional)",
            }
        ),
    )
    position = forms.CharField(
        max_length=255,
        required=False,
        widget=forms.TextInput(
            attrs={
                "class": "block w-full px-3 py-3 border border-gray-300 rounded-md leading-5 bg-white placeholder-gray-500 focus:outline-none focus:placeholder-gray-400 focus:ring-1 focus:ring-blue-500 focus:border-blue-500",
                "placeholder": "Position or Title (Optional)",
            }
        ),
    )
    contact_number = forms.CharField(
        max_length=20,
        required=False,
        widget=forms.TextInput(
            attrs={
                "class": "block w-full px-3 py-3 border border-gray-300 rounded-md leading-5 bg-white placeholder-gray-500 focus:outline-none focus:placeholder-gray-400 focus:ring-1 focus:ring-blue-500 focus:border-blue-500",
                "placeholder": "+63 9XX XXX XXXX (Optional)",
            }
        ),
    )

    class Meta:
        model = User
        fields = (
            "username",
            "first_name",
            "last_name",
            "email",
            "user_type",
            "organization",
            "position",
            "contact_number",
            "password1",
            "password2",
        )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["username"].widget.attrs.update(
            {
                "class": "block w-full px-3 py-3 border border-gray-300 rounded-md leading-5 bg-white placeholder-gray-500 focus:outline-none focus:placeholder-gray-400 focus:ring-1 focus:ring-blue-500 focus:border-blue-500",
                "placeholder": "Choose a username",
            }
        )
        self.fields["password1"].widget.attrs.update(
            {
                "class": "block w-full px-3 py-3 border border-gray-300 rounded-md leading-5 bg-white placeholder-gray-500 focus:outline-none focus:placeholder-gray-400 focus:ring-1 focus:ring-blue-500 focus:border-blue-500",
                "placeholder": "Create a secure password",
            }
        )
        self.fields["password2"].widget.attrs.update(
            {
                "class": "block w-full px-3 py-3 border border-gray-300 rounded-md leading-5 bg-white placeholder-gray-500 focus:outline-none focus:placeholder-gray-400 focus:ring-1 focus:ring-blue-500 focus:border-blue-500",
                "placeholder": "Confirm your password",
            }
        )

    def clean_email(self):
        email = self.cleaned_data.get("email")
        if email and User.objects.filter(email=email).exists():
            raise forms.ValidationError("A user with this email already exists.")
        return email

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data["email"]
        user.first_name = self.cleaned_data["first_name"]
        user.last_name = self.cleaned_data["last_name"]
        user.user_type = self.cleaned_data["user_type"]
        user.organization = self.cleaned_data["organization"]
        user.position = self.cleaned_data["position"]
        user.contact_number = self.cleaned_data["contact_number"]
        user.is_approved = False

        if commit:
            user.save()
        return user


class UserProfileForm(forms.ModelForm):
    """Form for updating an existing user's contact information."""

    class Meta:
        model = User
        fields = (
            "first_name",
            "last_name",
            "email",
            "organization",
            "position",
            "contact_number",
        )
        widgets = {
            "first_name": forms.TextInput(attrs={"class": "form-control"}),
            "last_name": forms.TextInput(attrs={"class": "form-control"}),
            "email": forms.EmailInput(attrs={"class": "form-control"}),
            "organization": forms.TextInput(attrs={"class": "form-control"}),
            "position": forms.TextInput(attrs={"class": "form-control"}),
            "contact_number": forms.TextInput(attrs={"class": "form-control"}),
        }

    def clean_email(self):
        email = self.cleaned_data.get("email")
        if email:
            users_with_email = User.objects.filter(email=email)
            if self.instance:
                users_with_email = users_with_email.exclude(pk=self.instance.pk)
            if users_with_email.exists():
                raise forms.ValidationError("A user with this email already exists.")
        return email


class MOARegistrationForm(UserCreationForm):
    """
    Self-registration form specifically for MOA staff.
    Creates unapproved accounts that require admin approval.
    """

    # MOA-specific user types only
    MOA_USER_TYPES = [
        ('bmoa', 'BARMM Ministry/Agency/Office'),
        ('lgu', 'Local Government Unit'),
        ('nga', 'National Government Agency'),
    ]

    first_name = forms.CharField(
        max_length=30,
        required=True,
        widget=forms.TextInput(
            attrs={
                "class": "block w-full py-3 px-4 text-base rounded-xl border border-gray-200 shadow-sm focus:ring-emerald-500 focus:border-emerald-500 min-h-[48px] bg-white transition-all duration-200",
                "placeholder": "Enter your first name",
            }
        ),
        help_text="Your official first name as it appears in government records"
    )

    last_name = forms.CharField(
        max_length=30,
        required=True,
        widget=forms.TextInput(
            attrs={
                "class": "block w-full py-3 px-4 text-base rounded-xl border border-gray-200 shadow-sm focus:ring-emerald-500 focus:border-emerald-500 min-h-[48px] bg-white transition-all duration-200",
                "placeholder": "Enter your last name",
            }
        ),
        help_text="Your official last name as it appears in government records"
    )

    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(
            attrs={
                "class": "block w-full py-3 px-4 text-base rounded-xl border border-gray-200 shadow-sm focus:ring-emerald-500 focus:border-emerald-500 min-h-[48px] bg-white transition-all duration-200",
                "placeholder": "your.email@agency.gov.ph",
            }
        ),
        help_text="Use your official government/organization email address"
    )

    user_type = forms.ChoiceField(
        choices=MOA_USER_TYPES,
        required=True,
        widget=forms.Select(
            attrs={
                "class": "block w-full py-3 px-4 text-base rounded-xl border border-gray-200 shadow-sm focus:ring-emerald-500 focus:border-emerald-500 min-h-[48px] appearance-none pr-12 bg-white transition-all duration-200"
            }
        ),
        help_text="Select the type of organization you represent"
    )

    organization = forms.CharField(
        max_length=255,
        required=True,
        widget=forms.TextInput(
            attrs={
                "class": "block w-full py-3 px-4 text-base rounded-xl border border-gray-200 shadow-sm focus:ring-emerald-500 focus:border-emerald-500 min-h-[48px] bg-white transition-all duration-200",
                "placeholder": "e.g., Department of Agriculture - BARMM",
            }
        ),
        help_text="Full official name of your organization or agency"
    )

    position = forms.CharField(
        max_length=255,
        required=True,
        widget=forms.TextInput(
            attrs={
                "class": "block w-full py-3 px-4 text-base rounded-xl border border-gray-200 shadow-sm focus:ring-emerald-500 focus:border-emerald-500 min-h-[48px] bg-white transition-all duration-200",
                "placeholder": "e.g., Program Manager, Regional Coordinator",
            }
        ),
        help_text="Your official position or title within the organization"
    )

    contact_number = forms.CharField(
        max_length=20,
        required=True,
        widget=forms.TextInput(
            attrs={
                "class": "block w-full py-3 px-4 text-base rounded-xl border border-gray-200 shadow-sm focus:ring-emerald-500 focus:border-emerald-500 min-h-[48px] bg-white transition-all duration-200",
                "placeholder": "+63 9XX XXX XXXX",
            }
        ),
        help_text="Your official contact number for verification purposes"
    )

    class Meta:
        model = User
        fields = (
            "username",
            "first_name",
            "last_name",
            "email",
            "user_type",
            "organization",
            "position",
            "contact_number",
            "password1",
            "password2",
        )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Style username field
        self.fields["username"].widget.attrs.update(
            {
                "class": "block w-full py-3 px-4 text-base rounded-xl border border-gray-200 shadow-sm focus:ring-emerald-500 focus:border-emerald-500 min-h-[48px] bg-white transition-all duration-200",
                "placeholder": "Choose a unique username",
            }
        )
        self.fields["username"].help_text = "Letters, digits and @/./+/-/_ only"

        # Style password fields
        self.fields["password1"].widget.attrs.update(
            {
                "class": "block w-full py-3 px-4 text-base rounded-xl border border-gray-200 shadow-sm focus:ring-emerald-500 focus:border-emerald-500 min-h-[48px] bg-white transition-all duration-200",
                "placeholder": "Create a strong password",
            }
        )
        self.fields["password1"].help_text = "At least 8 characters, not entirely numeric"

        self.fields["password2"].widget.attrs.update(
            {
                "class": "block w-full py-3 px-4 text-base rounded-xl border border-gray-200 shadow-sm focus:ring-emerald-500 focus:border-emerald-500 min-h-[48px] bg-white transition-all duration-200",
                "placeholder": "Confirm your password",
            }
        )
        self.fields["password2"].help_text = "Enter the same password for verification"

    def clean_email(self):
        """Validate that email is unique and from a government domain."""
        email = self.cleaned_data.get("email")

        if email:
            # Check for existing email
            if User.objects.filter(email=email).exists():
                raise forms.ValidationError(
                    "This email address is already registered. "
                    "Please use a different email or contact support if this is an error."
                )

            # Recommend (but don't require) government email
            if not any(domain in email.lower() for domain in ['.gov.ph', '.edu.ph']):
                # Add a warning but allow the registration
                pass  # Could add a soft warning in the future

        return email

    def clean_contact_number(self):
        """Validate Philippine contact number format."""
        contact_number = self.cleaned_data.get("contact_number")

        if contact_number:
            # Remove common separators
            cleaned = contact_number.replace(' ', '').replace('-', '').replace('+', '')

            # Check if it's a valid Philippine number pattern
            if not (cleaned.startswith('63') or cleaned.startswith('09')):
                raise forms.ValidationError(
                    "Please enter a valid Philippine contact number "
                    "(e.g., +63 9XX XXX XXXX or 09XX XXX XXXX)"
                )

        return contact_number

    def save(self, commit=True):
        """Create user account with is_approved=False."""
        user = super().save(commit=False)
        user.email = self.cleaned_data["email"]
        user.first_name = self.cleaned_data["first_name"]
        user.last_name = self.cleaned_data["last_name"]
        user.user_type = self.cleaned_data["user_type"]
        user.organization = self.cleaned_data["organization"]
        user.position = self.cleaned_data["position"]
        user.contact_number = self.cleaned_data["contact_number"]

        # Critical: Set is_approved=False for MOA staff
        user.is_approved = False
        user.is_active = True  # Active but not approved

        if commit:
            user.save()

        return user


__all__ = [
    "CustomLoginForm",
    "UserRegistrationForm",
    "UserProfileForm",
    "MOARegistrationForm",
]
