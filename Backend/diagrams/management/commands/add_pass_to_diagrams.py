import json
from django.core.management.base import BaseCommand
from diagrams.models import DiagramFrame, DiagramLogs
from django.contrib.auth import get_user_model


User = get_user_model()
class Command(BaseCommand):
    help = "Processes DiagramFrame objects and sets protection if conditions are met."

    def handle(self, *args, **options):
        user = User.objects.filter(username="s.kouider").first()
        # Loop through all DiagramFrame objects
        for diagram in DiagramFrame.objects.all():
            try:
                # Open and read the source file
                log = DiagramLogs.objects.create(diagram=diagram, user=user, path=diagram.source.path)
                with diagram.source.open('r') as file:
                    data = json.load(file)
                
                # Navigate to the passData section
                original_data = data.get("originalData", {})
                pass_data = original_data.get("passData", {})
                if "authenticationType" not in pass_data:
                    self.stdout.write(self.style.NOTICE(f"No authenticationType found in passData for diagram '{diagram.id}'. No action taken."))
                    continue
                # Check if the authenticationType is "Email/Password"
                if pass_data.get("authenticationType") == "Email/Password":
                    # Check if "Entire Admin Panel" is in the value array
                    if "Entire Admin Panel" in pass_data.get("value", []):
                        password = pass_data.get("password")
                        if password:
                            # Set the passkey and mark the diagram as protected
                            diagram.set_passkey(password)
                            diagram.is_protected = True
                            diagram.save()
                            log.changes = {"is_protected": {
                                "old": False,
                                "new": True
                            }}
                            log.save()
                            self.stdout.write(self.style.SUCCESS(f"Protected diagram '{diagram.id}' with passkey."))
                        else:
                            self.stdout.write(self.style.WARNING(f"No password found for diagram '{diagram.id}'."))
                    else:
                        self.stdout.write(self.style.NOTICE(f"'Entire Admin Panel' not found in passData for diagram '{diagram.id}'. No action taken."))
                else:
                    self.stdout.write(self.style.NOTICE(f"No action required for diagram '{diagram.id}'."))
            except Exception as e:
                self.stdout.write(self.style.ERROR(f"Error processing diagram '{diagram.id}': {str(e)}"))