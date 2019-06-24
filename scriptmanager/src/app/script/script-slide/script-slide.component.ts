import { Component, OnInit, Input, Output, EventEmitter } from '@angular/core';
import { FormGroup, FormControl } from '@angular/forms';
import * as ClassicEditor from '@ckeditor/ckeditor5-build-classic';

@Component({
  selector: 'app-script-slide',
  templateUrl: './script-slide.component.html',
  styleUrls: ['./script-slide.component.sass']
})
export class ScriptSlideComponent implements OnInit {
  @Input() slide: any;
  public oldSlide: any = [];
  @Input() index: number;
  @Output() removeSlideEmitter = new EventEmitter<number>();
  @Output() saveSlideEmitter = new EventEmitter<any>();
  @Input() view: boolean = false;
  public comment = false;
  editorForm: FormGroup;

  public Editor = ClassicEditor;
  public ckeditorConfig = {
    placeholder: 'Type the content here!'
  }


  constructor() { }

  public removeSlide() {
    this.removeSlideEmitter.emit(this.index);
  }

  public checkSlide() {
    this.oldSlide.cue = this.slide.cue;
    this.oldSlide.narration = this.slide.narration;
  }

  public saveSlide() {
    // console.log(this.oldSlide.cue)
    if (this.oldSlide.cue != this.slide.cue || this.oldSlide.narration != this.slide.narration) {
      this.slide.cue = this.editorForm.get('cue').value
      this.slide.narration = this.editorForm.get('narration').value
      this.saveSlideEmitter.emit(this.slide);
    }
    this.checkSlide()
  }

  cueKey(event) { this.slide.cue = event.target.value; }
  narrationKey(event) { this.slide.narration = event.target.value; }
  // handleSelection( val ){
  //   console.log(val)
  // }

  ngOnInit() {
    this.editorForm = new FormGroup({
      'cue': new FormControl(),
      'narration': new FormControl()
    })
    this.checkSlide()
  }

}
