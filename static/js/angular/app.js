(function() {

var AppCtrl = function($scope, $http, $location) {
  /**
   * The URL to query for condition information. Initialized in
   * highlight_root.html
   * @type {string}
   */
  $scope.loadUrl;
  /** @type {string} */

  /**
   * Source for the chart.
   * @type {string}
   */
  $scope.imgSrc = '';

  /** @type {number} */
  $scope.condition;
  /** @type {Array.<number>} */
  $scope.conditions;

  /** @type {number} */
  $scope.curConditionId;

  /**
   @type {{
     passed: {Array.<Reference>},
     failed: {Array.<Reference>},
     gold: {Array.<Reference>},
     combined: {Array.<Reference>}
   }}
   */
  $scope.allReferences;

  /** @type {Reference} */
  $scope.curReference;

  /** @type {Object.<string, (number|string)>} */
  $scope.filters = {
    workerIndex: 0,
    expandToSentence: false,
    /**
     * If true, require user to select all of the text in a reference before it is
     * highlighted.
     * @type {string} One of "strict", "lenient", "hybrid", or "sentence"
     */
    matchMode: 'lenient'
  };

  $scope.curMarksManager;
  $scope.curSpanManager;

  // Fetch the conditions
  $http.get('static/data/conditions.json').
      success(function(data, status, headers) {
        $scope.conditions = data;
        if (data.length > 0) {
          $scope.curConditionId = data[0];
          $scope.changeConditions();
        }
      });

  $scope.changeConditions = function() {
    if ($scope.curSpanManager) {
      $scope.curSpanManager.clearSpans();
    }

    // Load the new condition
    $http.get('static/data/' + $scope.curConditionId + '.json').
        success(function(data, status, headers) {
          // Reset the worker filter
          $scope.imgSrc = 'static/' + data.chart;
          $scope.curText = data.text;
          $scope.sentences = data.sentences;
          $scope.datatable = data.datatable;
          $scope.marks = data.marks;
          $scope.visualReferences = data.visual_references;
          $scope.allReferences = data.references;
          $scope.curReference = $scope.allReferences[0].reference;

          // Add names and select grouping to the references
          angular.forEach($scope.allReferences, function(reference) {
            switch(reference.type) {
              case 'gold':
                reference.name = 'Gold';
                reference.selectType = '';
                break;
              case 'combined':
                reference.name = 'Output';
                reference.selectType = '';
                break;
              default:
                reference.name = 'Worker ' + reference.worker_id;
                if (reference.type === 'passed') {
                  reference.selectType = 'Passed gold';
                } else {
                  reference.selectType = 'Failed gold';
                }
            }
          });
        });
  };

  $scope.updateCondition = function() {
    initReferences($scope);
  };

  $scope.onReferenceSelect = function(ref) {
    ref.selected = !ref.selected;
    var overlappedReferences = [];
    for (var i=0; i<$scope.curReference.length; i++) {
      var reference = $scope.curReference[i];
      if (reference.selected) {
        overlappedReferences.push(reference);
      }
    }
    highlightRelatedTuples($scope, overlappedReferences);
    highlightRelatedPhrases($scope, overlappedReferences);
  }

  angular.element(document.getElementById('theChart')).on('load',
      function() {
        initReferences($scope);
      });

  var textPar = angular.element(document.getElementById('theTextParagraph'));
  textPar.on('mousedown', function() {
    // Clear the spans
    if ($scope.curSpanManager) {
      $scope.curSpanManager.clearSpans();
    }
    // Clear the highlights
    $scope.curMarksManager.unhighlight();
    angular.forEach($scope.curReference, function(reference) {
      reference.selected = false;
    });
    $scope.$apply();
  });
  textPar.on('mouseup', function() {
    // Get the currently selected words
    var curSelection = window.getSelection();
    if (curSelection.type === 'Range') {
      var start = Math.min(curSelection.anchorOffset, curSelection.focusOffset);
      var end = Math.max(curSelection.anchorOffset, curSelection.focusOffset);
      var selection = {
        start: start,
        end: end
      };
      var references = $scope.curReference;
      var overlappedReferences;

      // Sentence mode
      if ($scope.filters.expandToSentence) {
        var expandedSelection = {
          'start': selection.start,
          'end': selection.end
        };
        angular.forEach($scope.sentences, function(sentence) {
          // Check for sentence overlap with the existing selection
          if ((selection.start >= sentence.start &&
               selection.start <= sentence.end) ||
              (selection.end >= sentence.start &&
               selection.end <= sentence.end)) {
            if (expandedSelection.start > sentence.start) {
              expandedSelection.start = sentence.start;
            }
            if (expandedSelection.end < sentence.end) {
              expandedSelection.end = sentence.end;
            }
          }
        });
        selection = expandedSelection;
      }

      if ($scope.filters.matchMode === 'strict') {
        overlappedReferences = getStrictRelatedReferences(
            selection, references);
      }
      else if ($scope.filters.matchMode === 'lenient') {
        overlappedReferences = getOverlappedReferences(selection, references);
      }
      // Hybrid
      else {
        overlappedReferences = getStrictRelatedReferences(
            selection, references);
        if (overlappedReferences.length === 0) {
          overlappedReferences = getOverlappedReferences(selection, references);
        }
      }

      highlightRelatedTuples($scope, overlappedReferences);
      highlightRelatedPhrases($scope, overlappedReferences, selection);
      $scope.$apply();
    }
  });
};

/**
 * Check if two sets of spans have any overlap.
 *
 * @param {Array.<{start: number, end: number}>} lspans .
 * @param {Array.<{start: number, end: number}>} rspans .
 * @returns {boolean} True if any of the spans overlap
 */
function hasOverlap(lspans, rspans) {
  var sortFunc = function(a,b) { return a.start - b.start; };
  lspans.sort(sortFunc);
  rspans.sort(sortFunc);

  var l = 0, r = 0;
  var overlaps = 0;
  var lspan, rspan;
  while (l < lspans.length && r < rspans.length) {
    lspan = lspans[l];
    rspan = rspans[r];
    // Case 1: left span ends before right span
    if (lspan.end <= rspan.start) {
      l += 1;
      continue;
    }

    // Case 2: right span ends before left span
    if (rspan.end <= lspan.start) {
      r += 1;
      continue;
    }

    return true;
  }
  return false;
};

/**
 * Find all the references which the highlighted phrase overlaps.
 *
 * @param {{start: number, end: number}} selection
 *    The indices of the selected text.
 * @returns {Array.<reference>} An array of references that the selection
 *    overlaps with.
 */
function getOverlappedReferences(selection, references) {
  var overlappedReferences = [];
  selection = [selection];
  references.forEach(function(reference) {
    reference.selected = false;
    if (hasOverlap(selection, reference.phrases)) {
      overlappedReferences.push(reference);
      reference.selected = true;
    }
  });
  return overlappedReferences;
};

function getStrictRelatedReferences(selection, references) {
  var relatedReferences = [];
  references.forEach(function(reference) {
    // Check if this reference is valid (the selection spans all the words in
    // the reference)
    reference.selected = false;
    var valid = true;
    reference.phrases.sort(function(a,b) { return a.start - b.start; });
    for (var i=0, l=reference.phrases.length; i < l; i++) {
      var phrase = reference.phrases[i];
      if (!(phrase.start >= selection.start && phrase.end <= selection.end)) {
        valid = false;
        break;
      }
    }
    if (valid) {
      reference.selected = true;
      relatedReferences.push(reference);
    }
  });
  return relatedReferences;
}


/**
 * Use the mark manager to highlight the tuples contained in the array of
 * references.
 *
 * @param {angular.Scope} $scope .
 * @param {Array.<reference>} references .
 */
function highlightRelatedTuples($scope, references) {
  // Determine the tuple IDs that the text references refer to.
  var referenced_tuples = [];
  var data = $scope.datatable.data;
  
  function matched_tuple(tuple_a, tuple_b) {
    return tuple_a.map(function(val, ind) {
      return val == tuple_b[ind]; // Match strings and floats that are the same number
    }).reduce(function(acc, val) { return acc && val; });
  }
  
  for(var i=0; i<references.length; i++) {
    for(var j=0; j<references[i].tuples.length; j++) {
      for(var k=0; k<data.length; k++) {
        if(matched_tuple(references[i].tuples[j], data[k].tuple)) {
          referenced_tuples.push(data[k].id);
          break;
        }
      }
    }
  }

  $scope.curMarksManager.highlight($scope.refMapper.getReferringMarks(
      referenced_tuples));
}

/**
 *
 * @param {{start: number, end: number}} [selection]
 */
function highlightRelatedPhrases($scope, references, selection) {

  // Highlight the phrases
  var phrases = [];
  references.forEach(function(reference) {
    // Deep copy the phrases, since we modify them later if there is a selection
    reference.phrases.forEach(function(phrase) {
      phrases.push({
        start: phrase.start,
        end: phrase.end
      });
    });
  });
  phrases.sort(function(a,b) { return a.start-b.start; });
  // Remove duplicates or merge
  var i=1;
  while (i < phrases.length) {
    if (phrases[i].start == phrases[i-1].start &&
        phrases[i].end == phrases[i-1].end) {
      phrases.splice(i, 1);
      continue;
    }
    if (phrases[i].start >= phrases[i-1].start &&
        phrases[i].start <= phrases[i-1].end) {
      phrases[i-1].end = Math.max(phrases[i].end, phrases[i-1].end);
      phrases.splice(i, 1);
      continue;
    }
    if (phrases[i].end >= phrases[i-1].start &&
       phrases[i].end <= phrases[i-1].end) {
      phrases[i-1].start = phrases[i].start;
      phrases.splice(i, 1);
      continue;
    }
    i++;
  }

  /** @type {Array.<{start: number, end: number}>} */
  var highlightAndReferenceSpans = [];
  var highlightSpans = [];

  // If there's a selection, modify the phrases to ignore the selection
  var i = 0;
  if (selection) {
    while (i < phrases.length) {
      // Completely contained within selection. Make three spans
      if (phrases[i].start >= selection.start &&
          phrases[i].end <= selection.end) {
        var before = {
          start: i === 0 ? selection.start :
              Math.max(selection.start, phrases[i-1].end),
          end: phrases[i].start
        };
        var after = {
          start: phrases[i].end,
          end: i >= phrases.length - 1 ? selection.end :
              Math.min(selection.end, phrases[i+1].start)
        };
        var currentPhrase = phrases[i];
        highlightAndReferenceSpans.push(currentPhrase);
        phrases.splice(i, 1);
        if (before.start !== before.end) {
          highlightSpans.push(before);
          phrases.splice(i, 0, before);
          i += 1;
        }
        phrases.splice(i, 0, currentPhrase);
        i += 1;
        if (after.start !== after.end) {
          highlightSpans.push(after);
          phrases.splice(i, 0, after);
          i += 1;
        }
        continue;
      }

      // Selection is completely contained in this phrase. Split and move on
      if (selection.start >= phrases[i].start &&
          selection.end <= phrases[i].end) {
        var before = {
          start: phrases[i].start,
          end: selection.start
        };
        var after = {
          start: selection.end,
          end: phrases[i].end
        };
        var selectionCopy = clone(selection);
        highlightAndReferenceSpans.push(selectionCopy);
        phrases.splice(i, 1);
        if (before.start !== before.end) {
          phrases.splice(i, 0, before);
          i += 1;
        }
        phrases.splice(i, 0, selectionCopy);
        i += 1;
        if (after.start !== after.end) {
          phrases.splice(i, 0, after);
          i += 1;
        }
        continue;
      }

      // Selection overlaps the end of the phrase
      if (phrases[i].end > selection.start &&
          phrases[i].end < selection.end) {
        var middle = {
          start: i === 0 ? selection.start :
              Math.max(selection.start, phrases[i-1].end),
          end: phrases[i].end
        };
        phrases[i].end = middle.start;

        phrases.splice(i, 0, middle);
        highlightAndReferenceSpans.push(middle);
        i++;
        
        var right = {
          start: middle.end,
          end: i >= phrases.length - 1 ? selection.end :
              Math.min(selection.end, phrases[i+1].start)
        }
        phrases.splice(i, 0, right);
        highlightSpans.push(right);
        i++;
        continue;

      }

      // Selection overlaps the start of the phrase
      if (phrases[i].start > selection.start &&
          phrases[i].start < selection.end) {

        var left = {
          start: i === 0 ? selection.start :
              Math.max(selection.start, phrases[i-1].end),
          end: phrases[i].start
        };

        phrases.splice(i, 0, left);
        highlightSpans.push(left);
        i++;
        
        var middle = {
          start: left.end,
          end: i >= phrases.length - 1 ? selection.end :
              Math.min(selection.end, phrases[i+1].start)
        }
        phrases[i].start = middle.end;
        phrases.splice(i, 0, middle);
        highlightAndReferenceSpans.push(middle);
        i++;
        continue;
      }

      i++;
    }
  }

  $scope.curSpanManager = createSpans(phrases, selection,
      highlightAndReferenceSpans, highlightSpans);
};

/**
 * Create spans in the paragraph from a set of phrases, and an optional
 * selection. The selection span is given a special class so it can be styled
 * separately.
 *
 * @param {Array.<{start: number, end: number}>} phrases A sorted array of
 *    phrases.
 * @param {{start: number, end: number}} [selection] An optional selection, to
 *    style differently.
 * @returns {SpanManager} The span manager used to create phrases.
 */
function createSpans(phrases, selection,
    highlightAndReferenceSpans, highlightSpans) {
  var paragraph = document.getElementById('theTextParagraph');

  // Create distinct spans
  i = 1;
  while(i < phrases.length) {
    // Phrases do not overlap
    if(phrases[i].start > phrases[i-1].end) {
      i++;
      continue;
    }
    
    // Phrases are identical
    if(phrases[i].start === phrases[i-1].start &&
       phrases[i].end === phrases[i-1].end) {
      phrases.splice(i,1);
      continue;
    }
    
    // Create at least two spans: the text before phrases[i]
    // and the overlap text between phrases[i-1] and phrases[i]
    var new_spans = [{
      'start': phrases[i-1].start,
      'end': phrases[i].start,
    }];
    
    // Case 1: phrase[i-1] contains phrase[i]
    if(phrases[i].end <= phrases[i-1].end) {
      new_spans.push(phrases[i]);
      // Case 1a: phrase[i-1] ends after phrase[i]
      if(phrases[i].end < phrases[i-1].end) {
        new_spans.push({
          'start': phrases[i].end,
          'end': phrases[i-1].end,
        });
      }
    }
    // Case 2: phrase[i-1] ends before phrase[i]							
    else if(phrases[i].end > phrases[i-1].end) {
      var new_tuple_ids = phrases[i-1].tuple_ids;
      new_spans.push({
        'start': phrases[i].start,
        'end': phrases[i-1].end,
      },
      {
        'start': phrases[i-1].end,
        'end': phrases[i].end,
      });
    }
    
    // Replace phrases[i-1] by the objects in new_spans
    phrases.splice.apply(phrases, new_spans.splice(0,0,i-1,1));
    
    i += new_spans.length-1;
  }
  // Add the selection to the phrases
  /*
  if (selection) {
    phrases.push(selection);
  }
  */
  phrases.sort(function(a,b) { return a.start-b.start; });

  // Create the spans in the text
  var sm = new SpanManager(paragraph);
  var spans = sm.createSpans(phrases, function(elem, span) {
    elem.setAttribute('class', 'text-reference');

    // Style the highlight and highlight/reference spans differently
    if (highlightAndReferenceSpans) {
      for (var i = 0, l = highlightAndReferenceSpans.length; i < l ; i++) {
        if (span.start == highlightAndReferenceSpans[i].start &&
            span.end == highlightAndReferenceSpans[i].end) {
          elem.setAttribute('class', 'text-reference text-reference-special');
        }
      }
    }
    if (highlightSpans) {
      for (var i = 0, l = highlightSpans.length; i < l ; i++) {
        if (span.start == highlightSpans[i].start &&
            span.end == highlightSpans[i].end) {
          elem.setAttribute('class', 'text-reference-special');
        }
      }
    }

    // Style the selection separate from regular references
    /*
    if (selection) {
      if (span.start == selection.start && span.end == selection.end) {
        elem.setAttribute('class', 'text-reference-special');
      }
    }
    */
  });
  return sm;
}

function initReferences($scope) {
  if($scope.curMarksManager) {
    $scope.curMarksManager.removeOverlay();
  }
  if($scope.curSpanManager) { $scope.curSpanManager.clearSpans(); }

  var datatable = $scope.datatable;
  var marks = $scope.marks;
  var visual_references = $scope.visualReferences;
  var text_references =  $scope.curReference;

  var refMapper = new ReferenceMapper(visual_references);
  
  // Merge the data tables
  var data = datatable.data,
    marksHash = {};
  var visrefs = visual_references.references.reduce(function(acc, val) {
    acc[val.mark_id] = val;
    return acc;
  }, {});
  visual_references.references.forEach(function(visual_reference) {
    visual_reference.tuple_ids.forEach(function(tuple_id) {
      marksHash[tuple_id] = { 'mark_id': visual_reference.mark_id };
    });
  });
  
  // Determine the tuple IDs that the text references refer to.
  var textrefs = text_references;
  var referenced_tuples = [];
  
  function matched_tuple(tuple_a, tuple_b) {
    return tuple_a.map(function(val, ind) {
      return val == tuple_b[ind]; // Match strings and floats that are the same number
    }).reduce(function(acc, val) { return acc && val; });
  }
  
  for(var i=0; i<textrefs.length; i++) {
    for(var j=0; j<textrefs[i].tuples.length; j++) {
      for(var k=0; k<data.length; k++) {
        if(matched_tuple(textrefs[i].tuples[j], data[k].tuple)) {
          if(!data[k].phrases) data[k].phrases = [];
          // Make a deep copy of the current phrase
          var new_phrase = clone(textrefs[i].phrases);
          data[k].phrases = data[k].phrases.concat(new_phrase);
          referenced_tuples.push(data[k]);
          break;
        }
      }
    }
  }
  
  // Add the marks that have associated text

  referenced_tuples.forEach(function(tuple) {
    tuple['mark'] = marksHash[tuple['id']];
    // Add a reference to the tuple to each mark that has a reference.
    // The marks manager uses this data to determine what marks
    // are referenced.
    marksHash[tuple['id']]['tuple'] = tuple;
  });
  $scope.reference_tuples = referenced_tuples;
  
  var marksManager = new MarksManager(marks.marks, document.getElementById('theChart'));
  marksManager.createOverlay();
  marksManager.changeType(MarksManager.DESATURATE);

  $scope.curMarksManager = marksManager;
  $scope.refMapper = refMapper;
}


var app = angular.module('visreferences', ['ui.bootstrap']);
app.config(function($locationProvider) {
  $locationProvider.html5Mode(true);
});

app.controller('AppCtrl', AppCtrl);

app.directive('referencedisplay', ReferenceDisplay);

function isArray(o) {
  return Object.prototype.toString.call(o) === '[object Array]';
}
function clone(obj) {
  if(!obj || typeof obj !== 'object') {
    return obj;
  }
  var out;
  // Arrays
  if(isArray(obj)) {
    out = [];
    for(var i=0; i<obj.length; i++) {
      out[i] = clone(obj[i]);
    }
  }
  else if(this instanceof Object) {						
    out = {};
    for(var attr in obj) {
      if(obj.hasOwnProperty(attr)) {
        out[attr] = clone(obj[attr]);
      }
    }
  }
  return out;	
}

}());
