from rest_framework import routers

from dice.apps.users.views import UserViewSet
from dice.apps.games.views import RoomViewSet, RoundViewSet, GameViewSet


router = routers.DefaultRouter()
router.register(r'users', UserViewSet)
router.register(r'rooms', RoomViewSet)
router.register(r'rounds', RoundViewSet)
router.register(r'games', GameViewSet)

urlpatterns = router.urls
