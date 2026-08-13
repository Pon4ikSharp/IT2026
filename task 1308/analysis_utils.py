def gotovnist (vitsotok_vtrat_nashih, boyova_gotovsint_nashig):
    if vitsotok_vtrat_nashih <= 30 and boyova_gotovsint_nashig >=80:
        return "We are Ready!"
    elif vitsotok_vtrat_nashih >=50 or boyova_gotovsint_nashig <=80:
        return "We are not ready"
