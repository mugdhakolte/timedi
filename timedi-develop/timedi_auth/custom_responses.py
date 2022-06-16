from django.utils.translation import ugettext_lazy as _

custom_responses = {"user": {201: _("User data saved successfully."),
                             200: _("User data updated successfully."),
                             204: _("User data deleted successfully.")
                             },

                    "hospital": {201: _("Main sheet data saved successfully."),
                                 200: _("Main sheet data updated successfully."),
                                 204: _("Hospital data deleted successfully.")
                                 },

                    "production-setting": {201: _("Production Setting data saved successfully."),
                                           200: _("Production Setting data updated successfully."),
                                           204: _("Production Setting data deleted successfully.")
                                           },

                    "intermediate-productions": {201: _("Intermediate Productions data saved successfully."),
                                                 200: _("Intermediate Productions data updated successfully."),
                                                 204: _("Intermediate Productions data deleted successfully.")
                                                 },

                    "stock-management": {201: _("Stock Management data saved successfully."),
                                         200: _("Stock Management data updated successfully."),
                                         204: _("Stock Management data deleted successfully.")
                                         },

                    "patient": {201: _("Patient data saved successfully."),
                                200: _("Patient data updated successfully."),
                                204: _("Patient data deleted successfully.")
                                },

                    "absence-reason": {201: _("Absence Reason data saved successfully."),
                                       200: _("Absence Reason data updated successfully."),
                                       204: _("Absence Reason data deleted successfully.")
                                       },

                    "patient-assign-module": {201: _("Assign Centre Module data saved successfully."),
                                              200: _("Assign Centre Module data updated successfully."),
                                              204: _("Assign Centre Module data deleted successfully.")
                                              },

                    "medicine": {201: _("Medicine data saved successfully."),
                                 200: _("Medicine data updated successfully."),
                                 204: _("Medicine data deleted successfully.")
                                 },
                    "medicine-planning": {201: _("Medicine Assigned to Patient."),
                                          200: _("Updated Medicine Assigned to Patient."),
                                          204: _("Deleted Medicine Assigned to Patient.")
                                          },
                    "planning": {201: _("Posology Planning saved successfully."),
                                 200: _("Posology Planning updated successfully."),
                                 204: _("Posology Planning deleted successfully.")
                                 },
                    "production": {201: _("Production saved successfully."),
                                   200: _("Production Planning updated successfully."),
                                   204: _("Production Planning deleted successfully.")
                                   },
                    "add-to-booklet": {200: _("Medicine added to booklet successfully."),
                                       },
                    }
