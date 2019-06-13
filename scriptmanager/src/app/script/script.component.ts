import { Component, OnInit, Input, Output, EventEmitter } from '@angular/core';
import {Router} from "@angular/router";
@Component({
  selector: 'app-script',
  templateUrl: './script.component.html',
  styleUrls: ['./script.component.sass']
})
export class ScriptComponent implements OnInit {
  @Input() slides: any;
  @Output() onSaveScript = new EventEmitter<any>();
  @Input() removedData: any;

  constructor(public router:Router) { }

  public addSlide() {
    this.slides.push(
      {
        id: '',
        cue: '',
        narration: '',
        order: '',
        script: ''
      }
    );
  }

  public onRemoveSlide(index) {
    if ( this.slides[index]['id'] != '' ) {
    this.removedData.push(this.slides[index]['id'])
    };
    this.slides.splice(index, 1);
  }

  public saveScript() {
    this.onSaveScript.emit(this.slides);
    // this.router.navigateByUrl("/")

    
  }

  ngOnInit() {
    this.addSlide();
  }

}
