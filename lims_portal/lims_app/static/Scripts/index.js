import { Pane } from 'https://cdn.skypack.dev/tweakpane@4.0.4';
import gsap from 'https://cdn.skypack.dev/gsap@3.12.0';
import ScrollTrigger from 'https://cdn.skypack.dev/gsap@3.12.0/ScrollTrigger';

const config = {
  theme: 'dark',
  animate: true, 
  snap: false,   
  start: 100, 
  end: 900, 
  scroll: true,
  debug: false
};

const ctrl = new Pane({
  title: 'Config',
  expanded: false
});

ctrl.hidden = true;

let items;
let scrollerScrub;
let dimmerScrub;
let chromaEntry;
let chromaExit;

const update = () => {
  document.documentElement.dataset.theme = config.theme;
  document.documentElement.dataset.syncScrollbar = config.scroll;
  document.documentElement.dataset.animate = config.animate;
  document.documentElement.dataset.snap = config.snap;
  document.documentElement.dataset.debug = config.debug;
  document.documentElement.style.setProperty('--start', config.start);
  document.documentElement.style.setProperty('--hue', config.start);
  document.documentElement.style.setProperty('--end', config.end);

  if (!config.animate) {
    var _chromaEntry, _chromaExit, _dimmerScrub, _scrollerScrub;
    (_chromaEntry = chromaEntry) && _chromaEntry.scrollTrigger.disable(true, false);
    (_chromaExit = chromaExit) && _chromaExit.scrollTrigger.disable(true, false);
    (_dimmerScrub = dimmerScrub) && _dimmerScrub.disable(true, false);
    (_scrollerScrub = scrollerScrub) && _scrollerScrub.disable(true, false);
    gsap.set(items, { opacity: 1 });
    gsap.set(document.documentElement, { '--chroma': 0 });
  } else {
    gsap.set(items, { opacity: i => i !== 0 ? 0.2 : 1 });
    dimmerScrub && dimmerScrub.enable(true, true);
    scrollerScrub && scrollerScrub.enable(true, true);
    chromaEntry && chromaEntry.scrollTrigger.enable(true, true);
    chromaExit && chromaExit.scrollTrigger.enable(true, true);
  }
};

const sync = event => {
  if (
  !document.startViewTransition ||
  event.target.controller.view.labelElement.innerText !== 'Theme')

  return update();
  document.startViewTransition(() => update());
};

ctrl.addBinding(config, 'animate', {
  label: 'Animate'
});

ctrl.addBinding(config, 'snap', {
  label: 'Snap'
});

ctrl.addBinding(config, 'start', {
  label: 'Hue Start',
  min: 0,
  max: 1000,
  step: 1
});

ctrl.addBinding(config, 'end', {
  label: 'Hue End',
  min: 0,
  max: 1000,
  step: 1
});

ctrl.addBinding(config, 'scroll', {
  label: 'Scrollbar'
});

ctrl.addBinding(config, 'debug', {
  label: 'Debug'
});

ctrl.addBinding(config, 'theme', {
  label: 'Theme',
  options: {
    System: 'system',
    Light: 'light',
    Dark: 'dark'
  }
});

ctrl.on('change', sync);
if (
!CSS.supports('(animation-timeline: scroll()) and (animation-range: 0% 100%)'))
{
  gsap.registerPlugin(ScrollTrigger);
  items = gsap.utils.toArray('ul li');

  gsap.set(items, { opacity: i => i !== 0 ? 0.2 : 1 });

  const dimmer = gsap.
  timeline().
  to(items.slice(1), {
    opacity: 1,
    stagger: 0.5 }).

  to(
  items.slice(0, items.length - 1),
  {
    opacity: 0.2,
    stagger: 0.5 },

   0);

  dimmerScrub = ScrollTrigger.create({
    trigger: items[0],
    endTrigger: items[items.length - 1],
    start: 'top top',
    end: 'bottom bottom',
    animation: dimmer,
    scrub: 0.2 });

  // register scrollbar changer
  const scroller = gsap.timeline().fromTo(
  document.documentElement,
  {
    '--hue': config.start },

  {
    '--hue': config.end,
    ease: 'none' });

  scrollerScrub = ScrollTrigger.create({
    trigger: items[0],
    endTrigger: items[items.length - 1],
    start: 'top top',
    end: 'bottom bottom',
    animation: scroller,
    scrub: 0.2 });

  chromaEntry = gsap.fromTo(
  document.documentElement,
  {
    '--chroma': 0 },

  {
    '--chroma': 0.3,
    ease: 'none',
    scrollTrigger: {
      scrub: 0.2,
      trigger: items[0],
      start: 'top top+=40',
      end: 'top top' } });

  chromaExit = gsap.fromTo(
  document.documentElement,
  {
    '--chroma': 0.3 },

  {
    '--chroma': 0,
    ease: 'none',
    scrollTrigger: {
      scrub: 0.2,
      trigger: items[items.length - 2],
      start: 'top top',
      end: 'top top-=40' } });

}
// run it
update();