from ..models import Trail, Trailhead, Report

def create_trail(name, region, coordinates):
  return Trail.objects.create(name=name, region=region, coordinates=coordinates)

def create_trailhead(trail, name, coordinates):
  return Trailhead.objects.create(trail=trail, name=name, coordinates=coordinates)

def create_report(report):
  return Report.objects.create(
    trail=report['trail'], trailhead=report['trailhead'], date_hiked=report['date_hiked'], day_hiked=report['day_hiked'], trail_begin=report['trail_begin'], trail_end=report['trail_end'], bathroom=report['bathroom'], pkg_location=report['pkg_location'], pkg_estimate_begin=report['pkg_estimate_begin'], pkg_estimate_end=report['pkg_estimate_end'], cars_seen=report['cars_seen'], people_seen=report['people_seen'], horses_seen=report['horses_seen'], dogs_seen=report['dogs_seen']
  )
