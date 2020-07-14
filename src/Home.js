import React, { useRef, useEffect } from 'react';
import clsx from 'clsx';

import { makeStyles, useTheme } from '@material-ui/core/styles';
import Drawer from '@material-ui/core/Drawer';
import CssBaseline from '@material-ui/core/CssBaseline';
import AppBar from '@material-ui/core/AppBar';
import Toolbar from '@material-ui/core/Toolbar';
import Typography from '@material-ui/core/Typography';
import Divider from '@material-ui/core/Divider';
import IconButton from '@material-ui/core/IconButton';
import Tooltip from '@material-ui/core/Tooltip';
import MenuIcon from '@material-ui/icons/Menu';
import MenuItem from '@material-ui/core/MenuItem';
import Menu from '@material-ui/core/Menu';
import List from '@material-ui/core/List';
import ListItem from '@material-ui/core/ListItem';
import ListItemIcon from '@material-ui/core/ListItemIcon';
import ListItemText from '@material-ui/core/ListItemText';
import CircularProgress from '@material-ui/core/CircularProgress';
import Grid from '@material-ui/core/Grid';

import MoreVertOutlined from '@material-ui/icons/MoreVertOutlined';
import LocationCity from '@material-ui/icons/LocationCity';
import Navigation from '@material-ui/icons/Navigation';
import SaveAlt from '@material-ui/icons/SaveAlt';
import ChevronLeftIcon from '@material-ui/icons/ChevronLeft';
import ChevronRightIcon from '@material-ui/icons/ChevronRight';

import { Map, TileLayer, GeoJSON } from 'react-leaflet';
import query_overpass from 'query-overpass';
import { saveSync } from 'save-file';
import utf8 from 'utf8';

import { AppContext } from './app_context';
const drawerWidth = 300;

const useStyles = makeStyles((theme) => ({
  root: {
    display: 'flex',
  },
  appBar: {
    transition: theme.transitions.create(['margin', 'width'], {
      easing: theme.transitions.easing.sharp,
      duration: theme.transitions.duration.leavingScreen,
    }),
  },
  appBarShift: {
    width: `calc(100% - ${drawerWidth}px)`,
    marginLeft: drawerWidth,
    transition: theme.transitions.create(['margin', 'width'], {
      easing: theme.transitions.easing.easeOut,
      duration: theme.transitions.duration.enteringScreen,
    }),
  },
  hide: {
    display: 'none',
  },
  drawer: {
    width: drawerWidth,
    flexShrink: 0,
  },
  drawerPaper: {
    width: drawerWidth,
  },
  drawerHeader: {
    display: 'flex',
    alignItems: 'center',
    padding: theme.spacing(0, 1),
    // necessary for content to be below app bar
    ...theme.mixins.toolbar,
    justifyContent: 'flex-end',
  },
  drawerTitle: {
    flexGrow: 1,
  },
  content: {
    flexGrow: 1,
    transition: theme.transitions.create('margin', {
      easing: theme.transitions.easing.sharp,
      duration: theme.transitions.duration.leavingScreen,
    }),
    marginLeft: -drawerWidth,
  },
  contentShift: {
    flexGrow: 1,
    padding: theme.spacing(3),
    transition: theme.transitions.create('margin', {
      easing: theme.transitions.easing.easeOut,
      duration: theme.transitions.duration.enteringScreen,
    }),
    marginLeft: 0,
  },
}));

export default function GameDrawer() {
  const classes = useStyles();
  const theme = useTheme();
  const [state, dispatch] = React.useContext(AppContext);
  const [anchorEl, setAnchorEl] = React.useState(null);
  const menuOpen = Boolean(anchorEl);
  const mapRef = useRef(null);
  const layerRef = useRef(null);

  const initialState = {
    latlng: {
      lat: 55.7558,
      lng: 37.6173,
    },
    geoJson: null,
    relationId: null,
    zoom: 6,
    drawerOpen: true,
    isSubmitting: false,
    errorMessage: null,
  };
  const [data, setData] = React.useState(initialState);

  const handleDrawerOpen = () => {
    setData({ ...data, drawerOpen: true });
  };
  const handleDrawerClose = () => {
    setData({ ...data, drawerOpen: false });
  };
  const handleMenuOpen = (event) => {
    setAnchorEl(event.currentTarget);
  };
  const handleMenuClose = () => {
    setAnchorEl(null);
  };
  const handleErrorClose = () => {
    setData({ ...data, errorMessage: null });
  }
  const showRelation = (id) => {
    setData({...data, isSubmitting: true});
    query_overpass(
      `[out:json][timeout:300]; ( relation(${id}); <; ); out geom;`,
      function (error, geoJson) {
        setData({ ...data, isSubmitting: false, errorMessage: error, relationId: id, geoJson: geoJson })
      },
      {}
    );
  }
  const handleSaveJson = () => {
    if (data.geoJson) {
      const js = utf8.encode(JSON.stringify(data.geoJson, null, 4));
      saveSync(js, `${data.relationId}.json`);
    }
    handleMenuClose();
  }
  const handleTraceRoad = () => {
    handleMenuClose();
  }

  useEffect(() => {
    if (mapRef && layerRef && data.geoJson) {
      mapRef.current.leafletElement.fitBounds(layerRef.current.leafletElement.getBounds());
    }
  }, [data]);

  return (
    <div className={classes.root}>
      <CssBaseline />
      <AppBar
        position="fixed"
        className={clsx(classes.appBar, {
          [classes.appBarShift]: data.drawerOpen,
        })}
      >
        <Toolbar>
          <IconButton
            color="inherit"
            aria-label="open drawer"
            onClick={handleDrawerOpen}
            edge="start"
            className={clsx(classes.menuButton, data.drawerOpen && classes.hide)}
          >
            <MenuIcon />
          </IconButton>
          <Typography variant="h6" noWrap className={classes.drawerTitle}>
            OSM test
          </Typography>
          <div>

          <IconButton
              aria-label="account of current user"
              aria-controls="menu-appbar"
              aria-haspopup="true"
              onClick={handleMenuOpen}
              color="inherit"
            >
              <MoreVertOutlined />
          </IconButton>

          <Menu
              id="menu-appbar"
              anchorEl={anchorEl}
              anchorOrigin={{
                vertical: 'top',
                horizontal: 'right',
              }}
              keepMounted
              transformOrigin={{
                vertical: 'top',
                horizontal: 'right',
              }}
              open={menuOpen}
              onClose={handleMenuClose}
            >
              <MenuItem onClick={handleSaveJson} disabled={data.isSubmitting || !data.geoJson}>
                Save JSON
              </MenuItem>
              <MenuItem onClick={handleTraceRoad} disabled={data.isSubmitting || !data.geoJson}>
                Trace road
              </MenuItem>
            </Menu>

          </div>
        </Toolbar>
      </AppBar>

      <Drawer
        className={classes.drawer}
        variant="persistent"
        anchor="left"
        open={data.drawerOpen}
        classes={{
          paper: classes.drawerPaper,
        }}>
        <div className={classes.drawerHeader}>
          <IconButton onClick={handleDrawerClose}>
            {theme.direction === 'ltr' ? <ChevronLeftIcon /> : <ChevronRightIcon />}
          </IconButton>
        </div>
        <Divider />

        <List>
          {state.relations.map(item => (
            <ListItem button key={item.id} disabled={data.isSubmitting} onClick={() => showRelation(item.id)}>
              <ListItemIcon>
                {data.isSubmitting 
                  ? <CircularProgress size={20} /> 
                  : item.type === 'city' 
                    ? <LocationCity />
                    : <Navigation />
                }
              </ListItemIcon>
              <ListItemText primary={item.ref} secondary={item.name} />
            </ListItem>
          )) 
        }
        </List>
      </Drawer>

      <main
        className={clsx(classes.content, {
          [classes.contentShift]: data.drawerOpen,
        })}
      >
        <div className={classes.drawerHeader} />
        <Map center={data.latlng} zoom={data.zoom} ref={mapRef}>
          <TileLayer
            attribution='&amp;copy <a href="http://osm.org/copyright">OpenStreetMap</a> contributors'
            url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
          />
          {data.geoJson ? <GeoJSON data={data.geoJson} key={data.relationId} ref={layerRef} /> : null}
        </Map>

      </main>

    </div>
  );
}
